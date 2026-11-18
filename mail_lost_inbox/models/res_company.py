# Copyright 2026 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = "res.company"

    lost_inbox_keep_catchall = fields.Boolean(
        string="Keep Catch-all Mail",
        default=False,
        help="Keep emails sent straight to the catch-all address in the lost "
        "mail inbox instead of bouncing them.",
    )
    lost_inbox_keep_automatic = fields.Boolean(
        string="Keep Automatic and Bulk Mail",
        default=False,
        help="Also keep automatic replies and bulk emails (Auto-Submitted, "
        "Precedence or X-Autoreply headers) in the lost mail inbox.",
    )
    lost_inbox_notify_group_id = fields.Many2one(
        "res.groups",
        string="Lost Mail Notification Group",
        help="Group notified when an email lands in the inbox and no routing "
        "rule handled it. Defaults to the Lost Mail manager group.",
    )
    lost_inbox_retention_days = fields.Integer(
        string="Lost Mail Retention (days)",
        default=30,
        help="Delete routed and discarded entries after this number of days. "
        "Set 0 to keep them forever.",
    )
    lost_inbox_pending_retention_days = fields.Integer(
        string="Pending Lost Mail Retention (days)",
        default=0,
        help="Delete pending entries after this number of days. "
        "Set 0 to keep them until they are routed or discarded.",
    )

    @api.constrains("lost_inbox_retention_days", "lost_inbox_pending_retention_days")
    def _check_lost_inbox_retention(self):
        for company in self:
            if (
                company.lost_inbox_retention_days < 0
                or company.lost_inbox_pending_retention_days < 0
            ):
                raise ValidationError(
                    _("Lost mail retention delays cannot be negative.")
                )
