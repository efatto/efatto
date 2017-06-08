# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_default_code = fields.Char(
        related='product_id.default_code',
        store=True,
    )

    _order = 'product_default_code desc'
