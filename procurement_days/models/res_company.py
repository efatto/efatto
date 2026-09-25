from odoo import fields, models


class Company(models.Model):
    _inherit = "res.company"

    procurement_days = fields.Integer(
        default=0,
        required=True,
        help="Security days for all procurements.",
    )
