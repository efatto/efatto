# -*- coding: utf-8 -*-

from openerp import models, api, exceptions, _


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.constrains('tax_id')
    def _check_single_order_line_tax(self):
        for order_line in self:
            if len(order_line.tax_id) > 1:
                raise exceptions.Warning(
                    _('Multiple Taxes Defined in line %s') % order_line.name)
