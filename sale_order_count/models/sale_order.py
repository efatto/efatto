# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def _sale_order_count(self):
        count = 0.0
        for line in self.order_line:
            if line.product_id.type in ['product', 'consu']:
                count += line.product_uom_qty
        self.sale_order_count = count

    sale_order_count = fields.Float(
        string='Total products of Sale Order',
        compute=_sale_order_count,
        )
