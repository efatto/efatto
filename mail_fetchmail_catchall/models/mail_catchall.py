# Copyright 2026 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models


class MailCatchall(models.Model):
    """Incoming email that no alias could route to a record.

    The original email is kept as a message of this thread, so its body and
    attachments remain available in the chatter.
    """

    _name = "mail.catchall"
    _description = "Catch-all Incoming Email"
    _inherit = ["mail.thread"]
    _order = "date desc, id desc"
    _rec_name = "name"

    name = fields.Char(string="Subject", readonly=True)
    email_from = fields.Char(string="From", readonly=True)
    email_to = fields.Char(string="To", readonly=True)
    date = fields.Datetime(
        string="Received Date",
        default=fields.Datetime.now,
        readonly=True,
        index=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    fetchmail_server_id = fields.Many2one(
        "fetchmail.server",
        string="Mail Server",
        readonly=True,
        index=True,
        ondelete="set null",
    )

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        values = {
            "name": msg_dict.get("subject") or _("No Subject"),
            "email_from": msg_dict.get("email_from"),
            "email_to": msg_dict.get("to"),
            "fetchmail_server_id": self.env.context.get("default_fetchmail_server_id"),
        }
        values.update(custom_values or {})
        return self.create(values)
