# Copyright 2026 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import itertools
import time
from datetime import timedelta
from email import policy
from email.message import EmailMessage
from unittest.mock import patch

from odoo import fields
from odoo.exceptions import AccessError, UserError
from odoo.tests.common import TransactionCase


class TestMailLostInbox(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.LostInbox = cls.env["mail.lost.inbox"]
        cls.Rule = cls.env["mail.lost.inbox.rule"]
        cls.catchall_alias = "catchall.test"
        cls.alias_domain_name = "example.com"
        cls.alias_domain = cls.env["mail.alias.domain"].create(
            {
                "name": cls.alias_domain_name,
                "catchall_alias": cls.catchall_alias,
            }
        )
        cls.company = cls.env.company
        cls.company.alias_domain_id = cls.alias_domain
        cls.company.write(
            {
                "lost_inbox_keep_catchall": False,
                "lost_inbox_keep_automatic": False,
                "lost_inbox_retention_days": 30,
                "lost_inbox_pending_retention_days": 0,
            }
        )
        cls.counter = itertools.count()

    def _make_email(
        self,
        subject,
        email_from,
        email_to,
        body="Email body",
        attachment=None,
        in_reply_to=None,
        references=None,
        extra_headers=None,
        with_message_id=True,
    ):
        message = EmailMessage(policy=policy.SMTP)
        message["Subject"] = subject
        message["From"] = email_from
        message["To"] = email_to
        if with_message_id:
            message["Message-Id"] = (
                f"<lost-mail-{next(self.counter)}-{int(time.time() * 1000)}"
                "@test.example.com>"
            )
        message["Date"] = "Tue, 01 Jan 2030 10:00:00 +0000"
        if in_reply_to:
            message["In-Reply-To"] = in_reply_to
        if references:
            message["References"] = references
        for header, value in (extra_headers or {}).items():
            message[header] = value
        message.set_content(body)
        if attachment:
            name, content = attachment
            message.add_attachment(
                content,
                maintype="application",
                subtype="octet-stream",
                filename=name,
            )
        return message.as_bytes()

    def _process(self, raw):
        return self.env["mail.thread"].message_process(False, raw)

    def _capture(self, subject="Lost email", email_from="sender@example.net"):
        raw = self._make_email(subject, email_from, "unknown@example.com")
        self._process(raw)
        return self.LostInbox.search([("subject", "=", subject)], limit=1)

    def test_capture_unroutable_email(self):
        raw = self._make_email(
            "Unknown alias",
            "Sender <sender@example.net>",
            "unknown-alias@example.com",
            body="Please route me",
            attachment=("report.txt", b"hello attachment"),
        )
        result = self._process(raw)
        self.assertFalse(result)
        lost = self.LostInbox.search([("subject", "=", "Unknown alias")])
        self.assertEqual(len(lost), 1)
        self.assertEqual(lost.state, "pending")
        self.assertEqual(lost.reason, "no_route")
        self.assertIn("sender@example.net", lost.email_from)
        self.assertIn("unknown-alias@example.com", lost.email_to)
        self.assertIn("Please route me", lost.body)
        self.assertIn("Message-Id", lost.headers)
        self.assertTrue(lost.raw_message)
        self.assertEqual(lost.company_id, self.company)
        self.assertEqual(len(lost.attachment_ids), 1)
        attachment = lost.attachment_ids
        self.assertEqual(attachment.name, "report.txt")
        self.assertEqual(attachment.datas, b"aGVsbG8gYXR0YWNobWVudA==")

    def test_duplicate_email_is_stored_once(self):
        raw = self._make_email("Duplicate", "sender@example.net", "unknown@example.com")
        self._process(raw)
        self._process(raw)
        self.assertEqual(
            self.LostInbox.search_count([("subject", "=", "Duplicate")]), 1
        )

    def test_duplicate_without_message_id_is_stored_once(self):
        raw = self._make_email(
            "No Message-Id",
            "sender@example.net",
            "unknown@example.com",
            with_message_id=False,
        )
        self._process(raw)
        self._process(raw)
        self.assertEqual(
            self.LostInbox.search_count([("subject", "=", "No Message-Id")]), 1
        )

    def test_routable_reply_is_not_captured(self):
        partner = self.env["res.partner"].create(
            {"name": "Known Customer", "email": "known@example.com"}
        )
        parent = partner.message_post(body="Original message", subject="Original")
        raw = self._make_email(
            "Re: Original",
            "known@example.com",
            "unknown@example.com",
            in_reply_to=parent.message_id,
            references=parent.message_id,
        )
        self._process(raw)
        self.assertFalse(self.LostInbox.search([("subject", "=", "Re: Original")]))
        self.assertEqual(
            self.env["mail.message"].search_count(
                [
                    ("model", "=", "res.partner"),
                    ("res_id", "=", partner.id),
                    ("subject", "=", "Re: Original"),
                ]
            ),
            1,
        )

    def test_catchall_bounced_by_default(self):
        raw = self._make_email(
            "Catch-all email",
            "sender@example.net",
            f"{self.catchall_alias}@{self.alias_domain_name}",
        )
        self._process(raw)
        self.assertFalse(self.LostInbox.search([("subject", "=", "Catch-all email")]))

    def test_catchall_kept_when_configured(self):
        self.company.lost_inbox_keep_catchall = True
        raw = self._make_email(
            "Catch-all email",
            "sender@example.net",
            f"{self.catchall_alias}@{self.alias_domain_name}",
        )
        self._process(raw)
        lost = self.LostInbox.search([("subject", "=", "Catch-all email")])
        self.assertEqual(len(lost), 1)
        self.assertEqual(lost.reason, "catchall")

    def test_catchall_bounce_not_captured(self):
        self.company.lost_inbox_keep_catchall = True
        raw = self._make_email(
            "Delivery Status Notification",
            "Mail Delivery System <mailer-daemon@example.net>",
            f"{self.catchall_alias}@{self.alias_domain_name}",
        )
        self._process(raw)
        self.assertFalse(
            self.LostInbox.search([("subject", "=", "Delivery Status Notification")])
        )

    def test_automatic_email_ignored_by_default(self):
        raw = self._make_email(
            "Out of office",
            "sender@example.net",
            "unknown@example.com",
            extra_headers={"Auto-Submitted": "auto-replied"},
        )
        with self.assertRaises(ValueError):
            self._process(raw)
        self.assertFalse(self.LostInbox.search([("subject", "=", "Out of office")]))

    def test_automatic_email_kept_when_configured(self):
        self.company.lost_inbox_keep_automatic = True
        raw = self._make_email(
            "Out of office",
            "sender@example.net",
            "unknown@example.com",
            extra_headers={"Auto-Submitted": "auto-replied"},
        )
        self._process(raw)
        lost = self.LostInbox.search([("subject", "=", "Out of office")])
        self.assertEqual(len(lost), 1)
        self.assertEqual(lost.state, "pending")

    def test_catchall_reply_is_routed_not_captured(self):
        self.company.lost_inbox_keep_catchall = True
        partner = self.env["res.partner"].create(
            {"name": "Catchall Customer", "email": "known@example.com"}
        )
        parent = partner.message_post(body="Original message", subject="Original")
        raw = self._make_email(
            "Re: Original",
            "known@example.com",
            f"{self.catchall_alias}@{self.alias_domain_name}",
            in_reply_to=parent.message_id,
            references=parent.message_id,
        )
        self._process(raw)
        self.assertFalse(self.LostInbox.search([("subject", "=", "Re: Original")]))

    def test_company_guessed_from_mail_domain(self):
        alias_domain = self.env["mail.alias.domain"].create(
            {"name": "lost.example.org"}
        )
        company = self.env["res.company"].create(
            {
                "name": "Mail Domain Company",
                "alias_domain_id": alias_domain.id,
            }
        )
        raw = self._make_email(
            "Other company email",
            "sender@example.net",
            "unknown@lost.example.org",
        )
        self._process(raw)
        lost = self.LostInbox.search([("subject", "=", "Other company email")])
        self.assertEqual(lost.company_id, company)

    def test_route_to_existing_record(self):
        lost = self._capture(subject="Route me")
        target = self.env["res.partner"].create(
            {"name": "Target Partner", "email": "target@example.com"}
        )
        message = lost._route_to_record(target, notify_followers=False)
        self.assertEqual(lost.state, "routed")
        self.assertEqual(lost.routed_model, "res.partner")
        self.assertEqual(lost.routed_res_id, target.id)
        self.assertEqual(lost.routed_message_id, message)
        self.assertEqual(message.model, "res.partner")
        self.assertEqual(message.res_id, target.id)
        self.assertEqual(message.message_id, lost.message_id)
        self.assertEqual(message.email_from, lost.email_from)
        self.assertIn("Route me", message.subject)
        self.assertFalse(lost.raw_message)
        self.assertEqual(lost.attachment_ids, self.env["ir.attachment"])

    def test_route_to_existing_record_keeps_attachment(self):
        raw = self._make_email(
            "Attachment email",
            "sender@example.net",
            "unknown@example.com",
            attachment=("data.txt", b"payload"),
        )
        self._process(raw)
        lost = self.LostInbox.search([("subject", "=", "Attachment email")])
        partner = self.env["res.partner"].create({"name": "Target"})
        message = lost._route_to_record(partner, notify_followers=False)
        self.assertEqual(len(message.attachment_ids), 1)
        self.assertEqual(message.attachment_ids.datas, b"cGF5bG9hZA==")

    def test_route_wizard_to_existing_record(self):
        lost = self._capture(subject="Wizard route")
        partner = self.env["res.partner"].create({"name": "Wizard Target"})
        wizard = (
            self.env["mail.lost.inbox.route"]
            .with_context(
                active_model="mail.lost.inbox",
                active_ids=lost.ids,
            )
            .create(
                {
                    "lost_inbox_ids": [(6, 0, lost.ids)],
                    "route_action": "record",
                    "target_record": "res.partner," + str(partner.id),
                    "notify_followers": False,
                }
            )
        )
        wizard.action_route()
        self.assertEqual(lost.state, "routed")
        self.assertEqual(lost.routed_res_id, partner.id)

    def test_route_wizard_default_get(self):
        first = self._capture(subject="Wizard default 1")
        second = self._capture(subject="Wizard default 2")
        wizard = (
            self.env["mail.lost.inbox.route"]
            .with_context(
                active_model="mail.lost.inbox",
                active_ids=(first + second).ids,
            )
            .new({})
        )
        self.assertEqual(set(wizard.lost_inbox_ids.ids), set((first + second).ids))

    def test_route_wizard_to_sender_contact(self):
        lost = self._capture(
            subject="New contact",
            email_from="New Sender <new.sender@example.net>",
        )
        wizard = (
            self.env["mail.lost.inbox.route"]
            .with_context(active_model="mail.lost.inbox", active_ids=lost.ids)
            .create(
                {
                    "lost_inbox_ids": [(6, 0, lost.ids)],
                    "route_action": "partner",
                    "create_partner": True,
                    "notify_followers": False,
                }
            )
        )
        wizard.action_route()
        self.assertEqual(lost.state, "routed")
        self.assertEqual(lost.routed_model, "res.partner")
        partner = self.env["res.partner"].browse(lost.routed_res_id)
        self.assertEqual(partner.email_normalized, "new.sender@example.net")

    def test_route_wizard_creates_record(self):
        lost = self._capture(subject="Create from email")
        partner_model = self.env["ir.model"]._get("res.partner")
        wizard = (
            self.env["mail.lost.inbox.route"]
            .with_context(active_model="mail.lost.inbox", active_ids=lost.ids)
            .create(
                {
                    "lost_inbox_ids": [(6, 0, lost.ids)],
                    "route_action": "new",
                    "new_model_id": partner_model.id,
                    "new_record_name": "Contact From Email",
                    "notify_followers": False,
                }
            )
        )
        wizard.action_route()
        self.assertEqual(lost.state, "routed")
        self.assertEqual(lost.routed_model, "res.partner")
        record = self.env["res.partner"].browse(lost.routed_res_id)
        self.assertEqual(record.name, "Contact From Email")

    def test_route_to_other_company_record_is_refused(self):
        lost = self._capture(subject="Other company target")
        other_company = self.env["res.company"].create({"name": "Other Company"})
        target = self.env["res.partner"].create(
            {"name": "Other company partner", "company_id": other_company.id}
        )
        with self.assertRaises(UserError):
            lost._route_to_record(target, notify_followers=False)

    def test_discard(self):
        lost = self._capture(subject="Discard me")
        lost.action_discard()
        self.assertEqual(lost.state, "discarded")
        self.assertTrue(lost.routed_date)

    def _create_lost_user(self, login="lost_mail_user", contact_manager=True):
        groups = [
            self.env.ref("base.group_user"),
            self.env.ref("mail_lost_inbox.group_lost_inbox_user"),
        ]
        if contact_manager:
            groups.append(self.env.ref("base.group_partner_manager"))
        return (
            self.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "Lost Mail User",
                    "login": login,
                    "email": f"{login}@example.com",
                    "groups_id": [(6, 0, [group.id for group in groups])],
                }
            )
        )

    def test_user_can_assign_and_route_but_not_edit_outcome(self):
        lost = self._capture(subject="User action")
        target = self.env["res.partner"].create({"name": "User Target"})
        user = self._create_lost_user()
        lost_user = lost.with_user(user)
        with self.assertRaises(AccessError):
            lost_user.write({"state": "discarded"})
        lost_user.write({"user_id": user.id})
        self.assertEqual(lost.user_id, user)
        lost_user._route_to_record(target, notify_followers=False)
        self.assertEqual(lost.state, "routed")
        self.assertEqual(lost.routed_res_id, target.id)

    def test_user_cannot_route_to_record_without_write_access(self):
        lost = self._capture(subject="No write access")
        target = self.env["res.partner"].create({"name": "Forbidden target"})
        user = self._create_lost_user(contact_manager=False)
        with self.assertRaises(AccessError):
            lost.with_user(user)._route_to_record(target, notify_followers=False)

    def test_capture_failure_raises_original_no_route_error(self):
        def _fail_capture(*args, **kwargs):
            raise Exception("capture failed")

        raw = self._make_email(
            "Capture failure",
            "sender@example.net",
            "unknown@example.com",
        )
        with patch.object(type(self.LostInbox), "_capture_message", _fail_capture):
            with self.assertRaises(ValueError):
                self._process(raw)
        self.assertFalse(self.LostInbox.search([("subject", "=", "Capture failure")]))

    def test_catchall_capture_failure_bounces_email(self):
        def _fail_capture(*args, **kwargs):
            raise Exception("capture failed")

        self.company.lost_inbox_keep_catchall = True
        raw = self._make_email(
            "Catch-all fallback",
            "sender@example.net",
            f"{self.catchall_alias}@{self.alias_domain_name}",
        )
        mail_thread = type(self.env["mail.thread"])
        with (
            patch.object(mail_thread, "_routing_create_bounce_email") as bounce,
            patch.object(type(self.LostInbox), "_capture_message", _fail_capture),
        ):
            self._process(raw)
        self.assertFalse(
            self.LostInbox.search([("subject", "=", "Catch-all fallback")])
        )
        self.assertTrue(bounce.called)

    def test_unlink_removes_attachments(self):
        raw = self._make_email(
            "Cascade attachment",
            "sender@example.net",
            "unknown@example.com",
            attachment=("cascade.txt", b"cascade"),
        )
        self._process(raw)
        lost = self.LostInbox.search([("subject", "=", "Cascade attachment")])
        attachments = lost.attachment_ids
        self.assertTrue(attachments)
        lost.unlink()
        self.assertFalse(attachments.exists())

    def test_uninstall_hook_removes_inbox_leftovers(self):
        from ..hooks import uninstall_hook

        lost = self._capture(subject="Uninstall leftovers")
        lost.message_post(body="A note", subtype_xmlid="mail.mt_note")
        attachments = (
            self.env["ir.attachment"]
            .sudo()
            .search(
                [
                    ("res_model", "=", "mail.lost.inbox"),
                    ("res_field", "in", [False, "raw_message"]),
                ]
            )
        )
        self.assertTrue(attachments)
        uninstall_hook(self.env)
        self.assertFalse(
            self.env["mail.message"].sudo().search([("model", "=", "mail.lost.inbox")])
        )
        self.assertFalse(
            self.env["ir.attachment"]
            .sudo()
            .search(
                [
                    ("res_model", "=", "mail.lost.inbox"),
                    ("res_field", "in", [False, "raw_message"]),
                ]
            )
        )

    # -----------------------------------------------------------------
    # Routing rules
    # -----------------------------------------------------------------

    def test_rule_discard_by_sender_domain(self):
        self.Rule.create(
            {
                "name": "Drop newsletter",
                "sender": "@news.example.net",
                "action": "discard",
                "company_id": self.company.id,
            }
        )
        lost = self._capture(subject="Newsletter", email_from="news@news.example.net")
        self.assertEqual(lost.state, "discarded")
        self.assertTrue(lost.rule_id)

    def test_rule_route_to_sender_contact(self):
        self.Rule.create(
            {
                "name": "VIP customers",
                "sender": "vip@customer.example",
                "action": "partner",
                "create_partner": True,
                "notify_followers": False,
                "company_id": self.company.id,
            }
        )
        lost = self._capture(subject="VIP", email_from="vip@customer.example")
        self.assertEqual(lost.state, "routed")
        self.assertEqual(lost.routed_model, "res.partner")
        partner = self.env["res.partner"].browse(lost.routed_res_id)
        self.assertEqual(partner.email_normalized, "vip@customer.example")

    def test_rule_route_to_fixed_record(self):
        target = self.env["res.partner"].create({"name": "Fixed Target"})
        self.Rule.create(
            {
                "name": "Fixed target",
                "subject_keyword": "fixed",
                "action": "record",
                "target_record": "res.partner," + str(target.id),
                "notify_followers": False,
                "company_id": self.company.id,
            }
        )
        lost = self._capture(subject="A fixed subject")
        self.assertEqual(lost.state, "routed")
        self.assertEqual(lost.routed_res_id, target.id)

    def test_rule_skipped_when_author_cannot_write_target(self):
        user = self._create_lost_user()
        restricted_target = self._create_lost_user(login="restricted_target")
        rule = self.Rule.create(
            {
                "name": "Restricted target",
                "subject_keyword": "restricted",
                "action": "partner",
                "company_id": self.company.id,
            }
        )
        rule.sudo().write({"create_uid": user.id, "write_uid": user.id})
        self.assertFalse(rule._check_user_access(restricted_target))

    def test_rule_assign(self):
        user = self.env.user
        self.Rule.create(
            {
                "name": "Assign accounting",
                "recipient": "@example.com",
                "action": "assign",
                "assign_user_id": user.id,
                "company_id": self.company.id,
            }
        )
        lost = self._capture(subject="Accounting email")
        self.assertEqual(lost.state, "pending")
        self.assertEqual(lost.user_id, user)

    def test_rule_does_not_match_other_company(self):
        other_company = self.env["res.company"].create({"name": "Other Company"})
        self.Rule.create(
            {
                "name": "Other company only",
                "sender": "@example.net",
                "action": "discard",
                "company_id": other_company.id,
            }
        )
        lost = self._capture(subject="Not for other company")
        self.assertEqual(lost.state, "pending")

    # -----------------------------------------------------------------
    # Retention
    # -----------------------------------------------------------------

    def test_cron_purges_processed_entries(self):
        lost = self._capture(subject="Old routed")
        target = self.env["res.partner"].create({"name": "Retention target"})
        lost._route_to_record(target, notify_followers=False)
        old_date = fields.Datetime.now() - timedelta(days=40)
        self.env.cr.execute(
            "UPDATE mail_lost_inbox SET routed_date = %s WHERE id = %s",
            (old_date, lost.id),
        )
        self.env.invalidate_all()
        self.LostInbox._cron_purge()
        self.assertFalse(lost.exists())

    def test_cron_keeps_recent_entries(self):
        lost = self._capture(subject="Recent routed")
        target = self.env["res.partner"].create({"name": "Recent target"})
        lost._route_to_record(target, notify_followers=False)
        self.LostInbox._cron_purge()
        self.assertTrue(lost.exists())

    def test_cron_purges_pending_entries_when_configured(self):
        self.company.lost_inbox_pending_retention_days = 5
        lost = self._capture(subject="Old pending")
        old_date = fields.Datetime.now() - timedelta(days=10)
        self.env.cr.execute(
            "UPDATE mail_lost_inbox SET create_date = %s WHERE id = %s",
            (old_date, lost.id),
        )
        self.env.invalidate_all()
        self.LostInbox._cron_purge()
        self.assertFalse(lost.exists())

    def test_cron_keeps_pending_entries_by_default(self):
        lost = self._capture(subject="Pending forever")
        old_date = fields.Datetime.now() - timedelta(days=400)
        self.env.cr.execute(
            "UPDATE mail_lost_inbox SET create_date = %s WHERE id = %s",
            (old_date, lost.id),
        )
        self.env.invalidate_all()
        self.LostInbox._cron_purge()
        self.assertTrue(lost.exists())
