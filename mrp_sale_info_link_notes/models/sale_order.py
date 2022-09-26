from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    production_notes = fields.Text()
    is_prototype = fields.Boolean()
