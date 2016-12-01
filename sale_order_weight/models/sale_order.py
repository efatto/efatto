# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, fields
import openerp.addons.decimal_precision as dp


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    weight = fields.Float(
        compute='_compute_weight',
        help="The weight is computed when the order "
        "is done.",
        digits_compute=dp.get_precision('Stock Weight'))
    net_weight = fields.Float(
        compute='_compute_weight',
        help="The weight is computed when the "
        "order is done.",
        digits_compute=dp.get_precision('Stock Weight'))
    volume = fields.Float(
        compute='_compute_weight',
        help="The volume is computed when the "
        "order is done.",
        digits_compute=dp.get_precision('Stock Weight'))
    weight_custom = fields.Float(
        help="Custom weight.",
        digits_compute=dp.get_precision('Stock Weight'))
    net_weight_custom = fields.Float(
        help="Custom net weight.",
        digits_compute=dp.get_precision('Stock Weight'))
    volume_custom = fields.Float(
        help="Custom volume.",
        digits_compute=dp.get_precision('Stock Weight'))
    compute_weight = fields.Boolean(default=True)

    @api.multi
    def _compute_weight(self):
        if self.compute_weight:
            self.net_weight = sum(
                l.product_id and l.product_id.weight_net or
                l.product_tmpl_id and l.product_tmpl_id.weight_net
                * l.product_uom_qty for l in self.order_line)
            self.weight = sum(
                l.product_id and l.product_id.weight or
                l.product_tmpl_id and l.product_tmpl_id.weight
                * l.product_uom_qty for l in self.order_line)
            self.volume = sum(
                l.product_id and l.product_id.volume or
                l.product_tmpl_id and l.product_tmpl_id.volume
                * l.product_uom_qty for l in self.order_line)
        else:
            self.net_weight = self.net_weight_custom
            self.weight = self.weight_custom
            self.volume = self.volume_custom