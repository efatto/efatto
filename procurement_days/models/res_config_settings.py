from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    procurement_days = fields.Float(
        related="company_id.procurement_days", string="Procurement Days", readonly=False
    )
