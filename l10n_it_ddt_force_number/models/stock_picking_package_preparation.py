from odoo import fields, models


class StockPickingPackagePreparation(models.Model):
    _inherit = 'stock.picking.package.preparation'

    date = fields.Date(
        states={'draft': [('readonly', False)],
                'done': [('readonly', False)],
                'in_pack': [('readonly', False)],
                'cancel': [('readonly', True)]})
