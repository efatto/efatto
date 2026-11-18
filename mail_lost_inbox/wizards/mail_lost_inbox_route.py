# Copyright 2026 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MailLostInboxRoute(models.TransientModel):
    """Route one or several lost emails to a chatter."""

    _name = "mail.lost.inbox.route"
    _description = "Route Lost Emails"

    lost_inbox_ids = fields.Many2many(
        "mail.lost.inbox",
        string="Lost Emails",
        required=True,
        default=lambda self: self._default_lost_inbox_ids(),
    )
    route_action = fields.Selection(
        selection=[
            ("record", "Attach to an Existing Record"),
            ("partner", "Attach to the Sender's Contact"),
            ("new", "Create a New Record"),
        ],
        string="Action",
        required=True,
        default="record",
    )
    target_record = fields.Reference(
        selection="_selection_target_record",
        string="Record",
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Contact",
        help="Leave empty to use the sender's contact of each email.",
    )
    create_partner = fields.Boolean(
        string="Create the Contact if Missing",
        default=True,
    )
    new_model_id = fields.Many2one(
        "ir.model",
        string="Record Type",
        domain=[("is_mail_thread", "=", True), ("transient", "=", False)],
    )
    new_record_name = fields.Char(
        string="Record Name",
        help="Used as record name when a single email is routed. "
        "Leave empty to use the email subject.",
    )
    notify_followers = fields.Boolean(
        default=True,
        help="Notify the followers of the target record. When disabled, the "
        "email is attached to the chatter without any notification.",
    )

    @api.model
    def _default_lost_inbox_ids(self):
        if self.env.context.get("active_model") == "mail.lost.inbox":
            return self.env["mail.lost.inbox"].browse(
                self.env.context.get("active_ids", [])
            )
        return self.env["mail.lost.inbox"]

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

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        lost_entries = self._default_lost_inbox_ids()
        if len(lost_entries) == 1:
            res.setdefault("lost_inbox_ids", [(6, 0, lost_entries.ids)])
            partner = lost_entries._find_sender_partner()
            if partner:
                res.setdefault("partner_id", partner.id)
        return res

    def _get_target_record(self):
        self.ensure_one()
        target = self.target_record
        if not target:
            raise UserError(_("Select the record to route the emails to."))
        if not hasattr(target, "message_post"):
            raise UserError(
                _("The selected record cannot receive messages on its chatter.")
            )
        target.check_access("write")
        return target

    def action_route(self):
        self.ensure_one()
        lost_entries = self.lost_inbox_ids.filtered(
            lambda lost: lost.state == "pending"
        )
        if not lost_entries:
            raise UserError(_("The selected emails were already routed or discarded."))
        if self.route_action == "record":
            target = self._get_target_record()
            for lost in lost_entries:
                lost._route_to_record(target, notify_followers=self.notify_followers)
        elif self.route_action == "partner":
            if self.create_partner and not self.partner_id:
                self.env["res.partner"].check_access("create")
            for lost in lost_entries:
                partner = self.partner_id or lost._find_sender_partner(
                    create=self.create_partner
                )
                if not partner:
                    raise UserError(
                        _(
                            "No contact found for the sender of the email "
                            "%(subject)s and contact creation is disabled."
                        )
                        % {"subject": lost.subject or _("(No Subject)")}
                    )
                lost._route_to_record(partner, notify_followers=self.notify_followers)
        elif self.route_action == "new":
            if not self.new_model_id:
                raise UserError(_("Select the type of record to create."))
            if len(lost_entries) > 1 and self.new_record_name:
                raise UserError(
                    _("A record name can only be set when routing a single email.")
                )
            for lost in lost_entries:
                record = lost._create_record(
                    self.new_model_id.model, self.new_record_name
                )
                lost._route_to_record(record, notify_followers=self.notify_followers)
        else:
            raise UserError(_("Select an action to perform."))
        return {
            "type": "ir.actions.act_window",
            "name": _("Lost Mail Inbox"),
            "res_model": "mail.lost.inbox",
            "view_mode": "kanban,tree,form",
            "domain": [("id", "in", lost_entries.ids)],
            "target": "current",
        }
