# Copyright 2026 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import _, api, fields, models, tools
from odoo.exceptions import AccessError, ValidationError

_logger = logging.getLogger(__name__)


class MailLostInboxRule(models.Model):
    """Automatic routing rule for lost emails."""

    _name = "mail.lost.inbox.rule"
    _description = "Lost Mail Routing Rule"
    _order = "sequence, id"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    sender = fields.Char(
        help="Comma-separated sender addresses or domains. Use @example.com "
        "or *@example.com to match a whole domain. Leave empty to ignore the "
        "sender.",
    )
    recipient = fields.Char(
        help="Comma-separated recipient addresses or domains. Use @example.com "
        "or *@example.com to match a whole domain. Leave empty to ignore the "
        "recipients.",
    )
    subject_keyword = fields.Char(
        string="Subject Keywords",
        help="Comma-separated keywords matched against the subject "
        "(case insensitive). Leave empty to ignore the subject.",
    )
    action = fields.Selection(
        selection=[
            ("partner", "Attach to the Sender's Contact"),
            ("record", "Attach to a Fixed Record"),
            ("discard", "Discard"),
            ("assign", "Assign to a User"),
        ],
        required=True,
        default="partner",
    )
    target_record = fields.Reference(
        selection="_selection_target_record",
    )
    create_partner = fields.Boolean(
        string="Create the Contact if Missing",
        default=False,
        help="When attaching to the sender's contact, create it when the sender "
        "is not an existing contact. Enable this only for trusted senders: "
        "the sender address comes from the email headers.",
    )
    assign_user_id = fields.Many2one("res.users")
    notify_followers = fields.Boolean(
        default=True,
        help="Notify the followers of the target record when the email is "
        "attached to it.",
    )

    @api.model
    def _selection_target_record(self):
        model_records = (
            self.env["ir.model"]
            .sudo()
            .search(
                [("is_mail_thread", "=", True), ("transient", "=", False)],
                order="name",
            )
        )
        return [(model.model, model.name) for model in model_records]

    @api.constrains("sender", "recipient", "subject_keyword")
    def _check_criteria(self):
        for rule in self:
            if not (rule.sender or rule.recipient or rule.subject_keyword):
                raise ValidationError(
                    _(
                        "Set at least one criterion (sender, recipient or subject "
                        "keyword) on the routing rule."
                    )
                )

    @api.constrains("action", "target_record", "assign_user_id")
    def _check_action_requirements(self):
        for rule in self:
            if rule.action == "record" and not rule.target_record:
                raise ValidationError(
                    _("Select a target record for the rule %s.") % rule.name
                )
            if rule.action == "assign" and not rule.assign_user_id:
                raise ValidationError(
                    _("Select a user to assign emails for the rule %s.") % rule.name
                )

    @api.model
    def _match_emails(self, patterns, emails):
        normalized_emails = {
            normalized
            for normalized in (tools.email_normalize(email) for email in emails)
            if normalized
        }
        for pattern in patterns.split(","):
            pattern = pattern.strip().lower()
            if not pattern:
                continue
            if pattern.startswith("*@"):
                pattern = pattern[1:]
            if pattern.startswith("@"):
                domain = pattern[1:]
                if any(
                    email.rsplit("@", 1)[1] == domain
                    for email in normalized_emails
                    if "@" in email
                ):
                    return True
            elif tools.email_normalize(pattern) in normalized_emails:
                return True
        return False

    def _match_lost(self, lost):
        """Return whether the rule matches ``lost`` (all criteria are ANDed)."""
        self.ensure_one()
        if self.company_id != lost.company_id:
            return False
        matched = False
        if self.sender:
            matched = True
            if not self._match_emails(self.sender, [lost.email_from]):
                return False
        if self.recipient:
            matched = True
            emails = (
                tools.email_split(lost.recipients)
                + tools.email_split(lost.email_to)
                + tools.email_split(lost.email_cc)
            )
            if not self._match_emails(self.recipient, emails):
                return False
        if self.subject_keyword:
            matched = True
            keywords = [
                keyword.strip().lower()
                for keyword in self.subject_keyword.split(",")
                if keyword.strip()
            ]
            subject = (lost.subject or "").lower()
            if not any(keyword in subject for keyword in keywords):
                return False
        return matched

    def _check_user_access(self, target):
        """Check that the rule author may write the target record."""
        self.ensure_one()
        user = self.write_uid or self.create_uid
        if not user:
            return True
        try:
            target.with_user(user).check_access("write")
        except AccessError:
            _logger.info(
                "Routing rule %s cannot write its target record as its author",
                self.id,
            )
            return False
        return True

    def _apply(self, lost):
        """Route ``lost`` according to the rule. Return True when handled."""
        self.ensure_one()
        if self.action == "discard":
            lost._discard(reason=self.name)
            return True
        if self.action == "assign":
            lost.write({"user_id": self.assign_user_id.id})
            try:
                with self.env.cr.savepoint():
                    lost._notify_users(self.assign_user_id)
            except Exception:
                _logger.exception(
                    "Could not notify the assignee of lost email %s", lost.id
                )
            return True
        if self.action == "partner":
            user = self.write_uid or self.create_uid
            if self.create_partner and user:
                try:
                    self.env["res.partner"].with_user(user).check_access("create")
                except AccessError:
                    _logger.info(
                        "Routing rule %s cannot create a contact as its author",
                        self.id,
                    )
                    return False
            partner = lost._find_sender_partner(create=self.create_partner)
            if not partner:
                _logger.info(
                    "Lost email %s matches rule %s but its sender has no contact",
                    lost.id,
                    self.id,
                )
                return False
            if not self._check_user_access(partner):
                return False
            lost._route_to_record(partner, notify_followers=self.notify_followers)
            return True
        if self.action == "record":
            target = self.target_record
            if not target:
                return False
            target_company = target._fields.get("company_id")
            if (
                target_company
                and target.company_id
                and target.company_id != lost.company_id
            ):
                _logger.info(
                    "Lost email %s matches rule %s but the target belongs to "
                    "another company",
                    lost.id,
                    self.id,
                )
                return False
            if not self._check_user_access(target):
                return False
            lost._route_to_record(target, notify_followers=self.notify_followers)
            return True
        return False
