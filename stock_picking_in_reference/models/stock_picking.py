from odoo import models, api, fields, exceptions


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    ddt_supplier_number = fields.Char(oldname='in_reference')
    ddt_supplier_date = fields.Date(oldname='in_date')
