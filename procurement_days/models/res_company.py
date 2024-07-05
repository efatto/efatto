from odoo import fields, models


class Company(models.Model):
    _inherit = "res.company"

    procurement_days = fields.Float(
        "Procurement Days",
        default=0.0,
        required=True,
        help="Security days for all procurements.",
    )
