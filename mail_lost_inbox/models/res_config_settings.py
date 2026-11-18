# Copyright 2026 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    lost_inbox_keep_catchall = fields.Boolean(
        related="company_id.lost_inbox_keep_catchall",
        readonly=False,
    )
    lost_inbox_keep_automatic = fields.Boolean(
        related="company_id.lost_inbox_keep_automatic",
        readonly=False,
    )
    lost_inbox_notify_group_id = fields.Many2one(
        related="company_id.lost_inbox_notify_group_id",
        readonly=False,
    )
    lost_inbox_retention_days = fields.Integer(
        related="company_id.lost_inbox_retention_days",
        readonly=False,
    )
    lost_inbox_pending_retention_days = fields.Integer(
        related="company_id.lost_inbox_pending_retention_days",
        readonly=False,
    )
