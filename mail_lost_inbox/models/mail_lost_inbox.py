# Copyright 2026 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
import hashlib
import logging
from datetime import timedelta

from markupsafe import Markup
from psycopg2 import IntegrityError

from odoo import Command, _, api, fields, models
from odoo.exceptions import AccessError, UserError
from odoo.tools import html_escape
from odoo.tools.mail import email_normalize, email_split

_logger = logging.getLogger(__name__)


class MailLostInbox(models.Model):
    """Incoming email that Odoo could not route to any record.

    The entry keeps everything needed to put the original message on a
    chatter later: body, headers, attachments and the Message-Id.
    """

    _name = "mail.lost.inbox"
    _description = "Lost Incoming Email"
    _inherit = ["mail.thread"]
    _order = "date desc, id desc"
    _rec_name = "name"
    _sql_constraints = [
        (
            "message_id_uniq",
            "unique(message_id)",
            "This email is already in the lost mail inbox.",
        )
    ]

    name = fields.Char(
        string="Title",
        compute="_compute_name",
        store=True,
        readonly=True,
    )
    subject = fields.Char(readonly=True)
    email_from = fields.Char(string="From", readonly=True)
    email_to = fields.Char(string="To", readonly=True)
    email_cc = fields.Char(string="Cc", readonly=True)
    recipients = fields.Char(
        string="All Recipients",
        readonly=True,
        help="Recipients extracted from the Delivered-To, To and Cc headers.",
    )
    email_domain = fields.Char(
        string="Sender Domain",
        compute="_compute_email_domain",
        store=True,
        readonly=True,
    )
    date = fields.Datetime(
        string="Received Date",
        default=fields.Datetime.now,
        readonly=True,
        index=True,
    )
    body = fields.Html(string="Message", readonly=True)
    headers = fields.Text(string="Original Headers", readonly=True)
    raw_message = fields.Binary(
        string="Original Email",
        attachment=True,
        copy=False,
        readonly=True,
    )
    message_id = fields.Char(string="Message-Id", readonly=True, index=True)
    reason = fields.Selection(
        selection=[
            ("no_route", "No Route Found"),
            ("catchall", "Sent to Catch-all Address"),
        ],
        required=True,
        default="no_route",
        readonly=True,
    )
    state = fields.Selection(
        selection=[
            ("pending", "Pending"),
            ("routed", "Routed"),
            ("discarded", "Discarded"),
        ],
        string="Status",
        required=True,
        default="pending",
        readonly=True,
        tracking=True,
        index=True,
    )
    user_id = fields.Many2one(
        "res.users",
        string="Responsible",
        tracking=True,
        help="User in charge of routing this email.",
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    rule_id = fields.Many2one(
        "mail.lost.inbox.rule",
        string="Routing Rule",
        readonly=True,
        ondelete="set null",
    )
    routed_model = fields.Char(string="Target Model", readonly=True)
    routed_res_id = fields.Integer(string="Target ID", readonly=True)
    routed_record_name = fields.Char(string="Target Record", readonly=True)
    routed_message_id = fields.Many2one(
        "mail.message",
        string="Routed Message",
        readonly=True,
        ondelete="set null",
    )
    routed_by = fields.Many2one("res.users", readonly=True)
    routed_date = fields.Datetime(string="Routed On", readonly=True)
    discard_reason = fields.Text(readonly=True)
    attachment_ids = fields.One2many(
        "ir.attachment",
        "res_id",
        string="Attachments",
        domain=[("res_model", "=", "mail.lost.inbox")],
        readonly=True,
    )
    attachment_count = fields.Integer(
        string="Inbox Attachments",
        compute="_compute_attachment_count",
    )

    @api.depends("subject")
    def _compute_name(self):
        for lost in self:
            lost.name = lost.subject or _("(No Subject)")

    @api.depends("email_from")
    def _compute_email_domain(self):
        for lost in self:
            email = email_normalize(lost.email_from)
            lost.email_domain = email.split("@")[1] if email and "@" in email else False

    @api.depends("attachment_ids")
    def _compute_attachment_count(self):
        for lost in self:
            lost.attachment_count = len(lost.attachment_ids)

    def write(self, vals):
        """Only managers may edit the routing outcome from the interface.

        Users change the responsible user and use the route/discard actions;
        those actions write with ``sudo()`` after checking the target record.
        """
        if (
            not self.env.su
            and not self.env.user.has_group("mail_lost_inbox.group_lost_inbox_manager")
            and set(vals) - {"user_id"}
        ):
            raise AccessError(
                _(
                    "You can only change the responsible user. "
                    "Use the Route or Discard actions to process an email."
                )
            )
        return super().write(vals)

    # ------------------------------------------------------------------
    # Capture of emails Odoo could not route
    # ------------------------------------------------------------------

    @api.model
    def _catchall_emails(self):
        alias_domains = self.env["mail.alias.domain"].sudo().search([])
        return {email.lower() for email in alias_domains.mapped("catchall_email")}

    @api.model
    def _message_to_list(self, message_dict):
        return [
            email_normalize(email) or email.lower()
            for email in email_split(message_dict.get("to") or "")
        ]

    @api.model
    def _is_direct_catchall(self, message_dict):
        """Return whether all recipients are catch-all addresses."""
        catchall_emails = self._catchall_emails()
        email_to_list = self._message_to_list(message_dict)
        return bool(catchall_emails and email_to_list) and all(
            email_to in catchall_emails for email_to in email_to_list
        )

    @api.model
    def _is_catchall(self, message_dict):
        """Return whether at least one recipient is a catch-all address."""
        catchall_emails = self._catchall_emails()
        email_to_list = self._message_to_list(message_dict)
        return bool(catchall_emails and email_to_list) and any(
            email_to in catchall_emails for email_to in email_to_list
        )

    @api.model
    def _should_keep_catchall(self, message_dict):
        company = self._guess_company(message_dict)
        return bool(company.lost_inbox_keep_catchall)

    @api.model
    def _is_automatic(self, message):
        """Return whether the message is an automatic or bulk email."""
        auto_submitted = (message.get("Auto-Submitted") or "").strip().lower()
        if auto_submitted and auto_submitted != "no":
            return True
        precedence = (message.get("Precedence") or "").strip().lower()
        if precedence in ("bulk", "junk", "list"):
            return True
        return bool(message.get("X-Autoreply") or message.get("X-Autorespond"))

    @api.model
    def _should_keep_automatic(self, message_dict):
        company = self._guess_company(message_dict)
        return bool(company.lost_inbox_keep_automatic)

    @api.model
    def _guess_company(self, message_dict):
        """Pick the company owning the recipient mail domain.

        Odoo 18 stores alias domains on ``mail.alias.domain`` linked to
        companies; the company email domain and the current company are the
        fallbacks.
        """
        Company = self.env["res.company"].sudo()
        domains = set()
        emails = email_split(
            message_dict.get("recipients") or message_dict.get("to") or ""
        )
        for email in emails:
            normalized = email_normalize(email)
            if normalized and "@" in normalized:
                domains.add(normalized.rsplit("@", 1)[1])
        if domains:
            alias_domains = (
                self.env["mail.alias.domain"]
                .sudo()
                .search([("name", "in", list(domains))], order="sequence, id")
            )
            for alias_domain in alias_domains:
                companies = alias_domain.company_ids
                if self.env.company in companies:
                    return self.env.company
                if companies:
                    return companies[:1]
            for company in Company.search([], order="id"):
                company_email = email_normalize(company.partner_id.email)
                if company_email and company_email.rsplit("@", 1)[1] in domains:
                    return company
        return self.env.company or Company.search([], limit=1)

    @api.model
    def _get_message_id(self, message, message_dict):
        if message.get("Message-Id"):
            return message_dict.get("message_id")
        # Core generates a new Message-Id for each delivery when the header is
        # missing; derive a stable one so redeliveries are deduplicated.
        digest = hashlib.sha1(message.as_bytes()).hexdigest()
        return f"<lost-{digest}@localhost>"

    @api.model
    def _prepare_lost_values(self, message, message_dict, company, reason):
        subject = message_dict.get("subject") or False
        headers = "\n".join(f"{header}: {value}" for header, value in message.items())
        message_id = self._get_message_id(message, message_dict)
        return {
            "name": subject or _("(No Subject)"),
            "subject": subject,
            "email_from": message_dict.get("email_from") or False,
            "email_to": message_dict.get("to") or False,
            "email_cc": message_dict.get("cc") or False,
            "recipients": message_dict.get("recipients") or False,
            "date": message_dict.get("date") or fields.Datetime.now(),
            "body": message_dict.get("body") or False,
            "headers": headers,
            "message_id": message_id,
            "raw_message": base64.b64encode(message.as_bytes()),
            "reason": reason,
            "company_id": company.id,
        }

    @api.model
    def _capture_message(self, message, message_dict, reason="no_route"):
        """Store an unroutable message in the inbox and apply routing rules."""
        message_id = self._get_message_id(message, message_dict)
        if message_id:
            existing = self.sudo().search([("message_id", "=", message_id)], limit=1)
            if existing:
                _logger.info(
                    "Email %s is already in the lost mail inbox (id %s)",
                    message_id,
                    existing.id,
                )
                return existing
        company = self._guess_company(message_dict)
        try:
            with self.env.cr.savepoint():
                lost = (
                    self.sudo()
                    .with_context(mail_create_nolog=True, mail_create_nosubscribe=True)
                    .create(
                        self._prepare_lost_values(
                            message, message_dict, company, reason
                        )
                    )
                )
        except IntegrityError:
            # A concurrent delivery created the same Message-Id.
            existing = self.sudo().search([("message_id", "=", message_id)], limit=1)
            if existing:
                return existing
            raise
        lost._create_attachments(message_dict.get("attachments") or [])
        lost._apply_rules()
        _logger.info(
            "Stored unroutable email %s from %s in the lost mail inbox (id %s)",
            lost.message_id,
            lost.email_from,
            lost.id,
        )
        return lost

    def _create_attachments(self, attachments):
        self.ensure_one()
        values = []
        for attachment in attachments:
            name = attachment[0] or "attachment"
            content = attachment[1]
            info = attachment[2] if len(attachment) > 2 else {}
            if isinstance(content, str):
                content = content.encode(info.get("encoding") or "utf-8")
            elif hasattr(content, "as_bytes"):
                content = content.as_bytes()
            if content is None:
                continue
            values.append(
                {
                    "name": name,
                    "datas": base64.b64encode(content),
                    "res_model": self._name,
                    "res_id": self.id,
                    "description": name,
                }
            )
        if values:
            self.env["ir.attachment"].sudo().create(values)

    # ------------------------------------------------------------------
    # Notifications
    # ------------------------------------------------------------------

    def _notify_users(self, users):
        self.ensure_one()
        partners = users.filtered(lambda user: user.active).mapped("partner_id")
        if not partners:
            return False
        subject = _("Unrouted email: %(subject)s") % {
            "subject": self.subject or _("(No Subject)"),
        }
        body = Markup(
            _(
                "<p>A new email could not be routed automatically.</p>"
                "<ul>"
                "<li><strong>From:</strong> %(email_from)s</li>"
                "<li><strong>To:</strong> %(email_to)s</li>"
                "<li><strong>Subject:</strong> %(subject)s</li>"
                "</ul>"
            )
            % {
                "email_from": html_escape(self.email_from or ""),
                "email_to": html_escape(self.email_to or ""),
                "subject": html_escape(self.subject or _("(No Subject)")),
            }
        )
        self.sudo().message_notify(
            partner_ids=partners.ids,
            subject=subject,
            body=body,
        )
        return True

    def _notify_new(self):
        """Notify the configured group that a new entry needs attention."""
        for lost in self:
            group = lost.company_id.lost_inbox_notify_group_id or self.env.ref(
                "mail_lost_inbox.group_lost_inbox_manager",
                raise_if_not_found=False,
            )
            if not group:
                continue
            users = (
                self.env["res.users"]
                .sudo()
                .search([("groups_id", "in", group.ids), ("active", "=", True)])
            )
            lost._notify_users(users)

    # ------------------------------------------------------------------
    # Routing rules
    # ------------------------------------------------------------------

    def _apply_rules(self):
        """Apply the first auto-routing rule matching the entry."""
        self.ensure_one()
        rules = (
            self.env["mail.lost.inbox.rule"]
            .sudo()
            .search(
                [("company_id", "=", self.company_id.id), ("active", "=", True)],
                order="sequence, id",
            )
        )
        rule = rules.filtered(lambda candidate: candidate._match_lost(self))[:1]
        if not rule:
            self._safe_notify_new()
            return False
        handled = False
        try:
            with self.env.cr.savepoint():
                handled = rule._apply(self)
                if handled:
                    self.write({"rule_id": rule.id})
        except Exception:
            _logger.exception(
                "Routing rule %s failed on lost email %s", rule.id, self.id
            )
            handled = False
        if not handled:
            self._safe_notify_new()
        return handled

    def _safe_notify_new(self):
        """Notify the group without letting a notification failure lose mail."""
        self.ensure_one()
        try:
            with self.env.cr.savepoint():
                self._notify_new()
        except Exception:
            _logger.exception("Could not notify about the lost email %s", self.id)

    # ------------------------------------------------------------------
    # Routing
    # ------------------------------------------------------------------

    def _find_sender_partner(self, create=False):
        self.ensure_one()
        if not self.email_from:
            return self.env["res.partner"]
        partners = (
            self.env["mail.thread"]
            .sudo()
            ._mail_find_partner_from_emails([self.email_from], force_create=create)
        )
        return partners[0] if partners else self.env["res.partner"]

    def _get_attachments_for_post(self):
        self.ensure_one()
        attachments = []
        for attachment in self.attachment_ids:
            if attachment.datas:
                attachments.append(
                    (attachment.name, base64.b64decode(attachment.datas))
                )
        return attachments

    def _get_message_dict(self):
        """Rebuild a ``message_dict`` accepted by ``message_new``/``message_post``."""
        self.ensure_one()
        return {
            "subject": self.subject or "",
            "email_from": self.email_from or "",
            "from": self.email_from or "",
            "to": self.email_to or "",
            "cc": self.email_cc or "",
            "recipients": self.recipients or "",
            "body": self.body or "",
            "date": self.date,
            "message_id": self.message_id or False,
            "attachments": self._get_attachments_for_post(),
        }

    def _post_silent_message(self, target, attachments, author):
        """Put the message on ``target`` without notifying its followers."""
        self.ensure_one()
        attachment_ids = []
        if attachments:
            values = [
                {
                    "name": name,
                    "datas": base64.b64encode(content),
                    "res_model": target._name,
                    "res_id": target.id,
                    "description": name,
                }
                for name, content in attachments
            ]
            attachment_ids = self.env["ir.attachment"].sudo().create(values).ids
        message = (
            self.env["mail.message"]
            .sudo()
            .create(
                {
                    "model": target._name,
                    "res_id": target.id,
                    "message_type": "email",
                    "subtype_id": self.env.ref("mail.mt_comment").id,
                    "body": Markup(self.body or ""),
                    "subject": self.subject or False,
                    "email_from": self.email_from or False,
                    "author_id": author.id if author else False,
                    "message_id": self.message_id or False,
                    "date": self.date,
                    "record_name": target.display_name,
                    "attachment_ids": [Command.set(attachment_ids)],
                }
            )
        )
        if (
            attachment_ids
            and "message_main_attachment_id" in target._fields
            and not target.message_main_attachment_id
        ):
            target.sudo().write({"message_main_attachment_id": attachment_ids[0]})
        return message

    def _route_to_record(self, target, notify_followers=True):
        """Move the email (body, author, date, Message-Id, attachments) to target."""
        self.ensure_one()
        if not target:
            raise UserError(_("Select a record to route the email to."))
        target = target.with_env(self.env)
        if not hasattr(target, "message_post"):
            raise UserError(
                _("The selected record cannot receive messages on its chatter.")
            )
        if (
            "company_id" in target._fields
            and target.company_id
            and target.company_id != self.company_id
        ):
            raise UserError(_("The selected record belongs to another company."))
        if not self.env.su:
            target.check_access("write")
        author = self._find_sender_partner()
        attachments = self._get_attachments_for_post()
        email_from = (
            self.email_from
            or (author.email_normalized if author else False)
            or self.env.user.partner_id.email_normalized
        )
        post_values = {
            "body": Markup(self.body or ""),
            "subject": self.subject or False,
            "message_type": "email",
            "subtype_xmlid": "mail.mt_comment",
            "email_from": email_from,
            "author_id": author.id if author else False,
            "message_id": self.message_id or False,
            "date": self.date,
        }
        if notify_followers:
            if attachments:
                post_values["attachments"] = attachments
            message = target.message_post(**post_values)
        else:
            message = self._post_silent_message(target, attachments, author)
        self.sudo().write(
            {
                "state": "routed",
                "routed_model": target._name,
                "routed_res_id": target.id,
                "routed_record_name": target.display_name,
                "routed_message_id": message.id,
                "routed_by": self.env.user.id,
                "routed_date": fields.Datetime.now(),
            }
        )
        # The message now belongs to the target: drop the inbox copy.
        self.attachment_ids.sudo().unlink()
        self.sudo().write({"raw_message": False})
        self._message_log(
            body=_("Email routed to %(record)s.")
            % {"record": html_escape(target.display_name)}
        )
        return message

    def _create_record(self, model_name, record_name=None):
        """Create a record of ``model_name`` from the email, like the gateway does."""
        self.ensure_one()
        Model = self.env[model_name].with_context(
            mail_create_nosubscribe=True, mail_create_nolog=True
        )
        custom_values = {}
        if record_name:
            name_field = Model._rec_name or "name"
            if name_field in Model._fields:
                custom_values[name_field] = record_name
        return Model.message_new(self._get_message_dict(), custom_values)

    def _discard(self, reason=False):
        for lost in self:
            if lost.state != "pending":
                continue
            lost.sudo().write(
                {
                    "state": "discarded",
                    "discard_reason": reason or False,
                    "routed_by": self.env.user.id,
                    "routed_date": fields.Datetime.now(),
                }
            )
            lost._message_log(body=_("Email discarded from the lost mail inbox."))
        return True

    def action_discard(self):
        self._discard()
        return True

    def action_open_target(self):
        self.ensure_one()
        if not self.routed_model or not self.routed_res_id:
            return False
        return {
            "type": "ir.actions.act_window",
            "name": self.routed_record_name or _("Target Record"),
            "res_model": self.routed_model,
            "res_id": self.routed_res_id,
            "view_mode": "form",
            "target": "current",
        }

    # ------------------------------------------------------------------
    # Retention
    # ------------------------------------------------------------------

    @api.model
    def _cron_purge(self):
        now = fields.Datetime.now()
        for company in self.env["res.company"].sudo().search([]):
            retention_days = company.lost_inbox_retention_days
            if retention_days > 0:
                limit = now - timedelta(days=retention_days)
                domain = [
                    ("company_id", "=", company.id),
                    ("state", "in", ("routed", "discarded")),
                    ("routed_date", "<", limit),
                ]
                self._purge_entries(domain, company)
            pending_days = company.lost_inbox_pending_retention_days
            if pending_days > 0:
                limit = now - timedelta(days=pending_days)
                domain = [
                    ("company_id", "=", company.id),
                    ("state", "=", "pending"),
                    ("create_date", "<", limit),
                ]
                self._purge_entries(domain, company)
        return True

    @api.model
    def _purge_entries(self, domain, company):
        """Delete entries matching domain in batches to keep memory bounded."""
        while True:
            entries = self.sudo().search(domain, limit=1000)
            if not entries:
                return
            _logger.info(
                "Purging %s lost mail entries for company %s",
                len(entries),
                company.id,
            )
            entries.unlink()
