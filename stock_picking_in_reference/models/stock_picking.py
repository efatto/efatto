from odoo import models, api, fields, exceptions


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    in_reference = fields.Char()
    in_date = fields.Date()
