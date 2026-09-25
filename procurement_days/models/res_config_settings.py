from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    procurement_days = fields.Integer(
        related="company_id.procurement_days",
        readonly=False,
    )
