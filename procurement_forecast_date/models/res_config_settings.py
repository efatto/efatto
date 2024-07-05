from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    forecast_lead = fields.Float(
        related="company_id.forecast_lead", string="Forecast Lead Days", readonly=False
    )
