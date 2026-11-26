# Copyright 2026 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import itertools
from email import policy
from email.message import EmailMessage

from odoo.tests.common import TransactionCase


class TestMailFetchmailCatchall(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.counter = itertools.count()
        cls.partner_model = cls.env["ir.model"]._get("res.partner")
        cls.server = cls.env["fetchmail.server"].create(
            {
                "name": "Catch-all server",
                "server_type": "imap",
                "state": "done",
            }
        )

    def _make_email(
        self,
        subject="Lost email",
        email_from="sender@example.net",
        email_to="unknown@example.com",
    ):
        message = EmailMessage(policy=policy.SMTP)
        message["Subject"] = subject
        message["From"] = email_from
        message["To"] = email_to
        message["Message-Id"] = f"<catchall-{next(self.counter)}@test.example.com>"
        message.set_content("Email body")
        return message.as_bytes()

    def _process(self, raw, model=False):
        return (
            self.env["mail.thread"]
            .with_context(default_fetchmail_server_id=self.server.id)
            .message_process(model, raw)
        )

    def _create_alias_domain(self):
        alias_domain = self.env["mail.alias.domain"].create(
            {
                "name": "catchall.example.com",
                "catchall_alias": "catchall",
            }
        )
        self.env.company.alias_domain_id = alias_domain
        return alias_domain

    def test_unroutable_email_is_stored(self):
        raw = self._make_email(subject="Unroutable email")
        res_id = self._process(raw)
        lost = self.env["mail.catchall"].browse(res_id)
        self.assertTrue(lost.exists())
        self.assertEqual(lost.name, "Unroutable email")
        self.assertEqual(lost.email_from, "sender@example.net")
        self.assertEqual(lost.email_to, "unknown@example.com")
        self.assertEqual(lost.fetchmail_server_id, self.server)
        self.assertEqual(len(lost.message_ids), 1)
        self.assertIn("Email body", lost.message_ids.body)

    def test_catchall_alias_email_is_stored(self):
        alias_domain = self._create_alias_domain()
        raw = self._make_email(
            subject="Catch-all alias email",
            email_to=f"catchall@{alias_domain.name}",
        )
        res_id = self._process(raw)
        lost = self.env["mail.catchall"].browse(res_id)
        self.assertTrue(lost.exists())
        self.assertEqual(lost.name, "Catch-all alias email")

    def test_object_id_catches_unroutable_email(self):
        self.server.object_id = self.partner_model
        raw = self._make_email(subject="Partner from unroutable email")
        res_id = self._process(raw, model=self.partner_model.model)
        partner = self.env["res.partner"].browse(res_id)
        self.assertEqual(partner.name, "Partner from unroutable email")
        self.assertFalse(
            self.env["mail.catchall"].search(
                [("name", "=", "Partner from unroutable email")]
            )
        )

    def test_object_id_catches_catchall_alias_email(self):
        alias_domain = self._create_alias_domain()
        self.server.object_id = self.partner_model
        raw = self._make_email(
            subject="Partner from catch-all alias",
            email_to=f"catchall@{alias_domain.name}",
        )
        res_id = self._process(raw, model=self.partner_model.model)
        partner = self.env["res.partner"].browse(res_id)
        self.assertEqual(partner.name, "Partner from catch-all alias")
        self.assertFalse(
            self.env["mail.catchall"].search(
                [("name", "=", "Partner from catch-all alias")]
            )
        )

    def test_object_id_does_not_intercept_alias_email(self):
        alias_domain = self._create_alias_domain()
        self.env["mail.alias"].create(
            {
                "alias_name": "support",
                "alias_domain_id": alias_domain.id,
                "alias_model_id": self.partner_model.id,
                "alias_defaults": "{'function': 'Alias route'}",
            }
        )
        self.server.object_id = self.partner_model
        raw = self._make_email(
            subject="Alias routed email",
            email_to=f"support@{alias_domain.name}",
        )
        res_id = self._process(raw, model=self.partner_model.model)
        partner = self.env["res.partner"].browse(res_id)
        self.assertEqual(partner.name, "Alias routed email")
        self.assertEqual(partner.function, "Alias route")

    def test_no_fetchmail_context_keeps_standard_behaviour(self):
        raw = self._make_email(subject="Not from fetchmail")
        with self.assertRaises(ValueError):
            self.env["mail.thread"].message_process(False, raw)
        self.assertFalse(
            self.env["mail.catchall"].search([("name", "=", "Not from fetchmail")])
        )
