from odoo import models, fields


class StockPickingPackagePreparation(models.Model):
    _inherit = "stock.picking.package.preparation"

    # ddt_number = fields.Char(states={'draft': [('readonly', False)]}) solo su xml
    # date = fields.Date(
    #     states={'draft': [('readonly', False)],
    #             'done': [('readonly', False)],
    #             'in_pack': [('readonly', False)],
    #             'cancel': [('readonly', True)]})
