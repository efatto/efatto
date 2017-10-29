# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import fields, models, api, _


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.multi
    def _set_sign_product_qty(self):
        for move in self:
            move.qty = move.product_uom_qty * (
                -1 if move.location_dest_id.usage in [
                    'customer', 'inventory', 'production', 'procurement'
                ] else 1)

    qty_available = fields.Float(
        related='product_id.qty_available',
    )
    virtual_available = fields.Float(
        related='product_id.virtual_available',
    )
    qty = fields.Float(
        compute='_set_sign_product_qty',
    )
    picking_partner_id = fields.Many2one(
        'res.partner', string='Picking Partner', store=True,
        related='picking_id.partner_id', help='Partner of the picking')
    product_code = fields.Char(
        string='Product Code',
        related='product_id.default_code'
    )