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
        help="The weight is computed when the order is done.",
        digits_compute=dp.get_precision('Stock Weight'))
    net_weight = fields.Float(
        compute='_compute_weight',
        help="The weight is computed when the order is done.",
        digits_compute=dp.get_precision('Stock Weight'))
    volume = fields.Float(
        compute='_compute_weight',
        help="The volume is computed when the order is done.",
        digits_compute=dp.get_precision('Stock Weight'))
    weight_custom = fields.Float(
        help="Put here weight when computed amount is not exact.",
        digits_compute=dp.get_precision('Stock Weight'))
    net_weight_custom = fields.Float(
        help="Put here net weight when computed amount is not exact.",
        digits_compute=dp.get_precision('Stock Weight'))
    volume_custom = fields.Float(
        help="Put here net volume when computed amount is not exact.",
        digits_compute=dp.get_precision('Stock Weight'))
    compute_weight = fields.Boolean(default=True)

    @api.multi
    def _compute_weight(self):
        for order in self:
            if order.compute_weight:
                order.net_weight = sum(
                    l.product_id.weight_net and l.product_id.weight_net or
                    l.product_tmpl_id.weight_net and l.product_tmpl_id.weight_net
                    * l.product_uom_qty for l in order.order_line)
                order.weight = sum(
                    l.product_id.weight and l.product_id.weight or
                    l.product_tmpl_id.weight and l.product_tmpl_id.weight
                    * l.product_uom_qty for l in order.order_line)
                order.volume = sum(
                    l.product_id.volume and l.product_id.volume or
                    l.product_tmpl_id.volume and l.product_tmpl_id.volume
                    * l.product_uom_qty for l in order.order_line)
            else:
                order.net_weight = order.net_weight_custom
                order.weight = order.weight_custom
                order.volume = order.volume_custom
