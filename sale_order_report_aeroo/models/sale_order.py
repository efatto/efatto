# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    print_hide_prices = fields.Boolean(string='Hide prices in report?')
