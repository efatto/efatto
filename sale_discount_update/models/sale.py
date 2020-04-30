# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    discount = fields.Float(
        help='This discount will affect all order lines on click of the '
             '"Update discount" button.')

    @api.multi
    @api.depends('discount', 'order_line')
    def sale_discount_update(self):
        for order in self:
            for line in order.order_line:
                line.discount = order.discount
