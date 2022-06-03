# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def _sale_order_count(self):
        for order in self:
            count = 0.0
            for line in order.order_line:
                if line.product_id.type in ['product', 'consu']:
                    count += line.product_uom_qty
            order.total_products_order = count

    total_products_order = fields.Float(
        compute=_sale_order_count,
        help=_('Sum of stockable and consumable product of the order'),
        )
