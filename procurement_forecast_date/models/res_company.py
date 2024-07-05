
from odoo import fields, models


class Company(models.Model):
    _inherit = 'res.company'

    forecast_lead = fields.Float(
        'Forecast Lead Time', default=0.0, required=True,
        help="Security days for all procurements.")
