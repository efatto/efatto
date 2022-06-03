# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import fields, models, api


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    is_delivery = fields.Boolean(
        string='Is a Delivery',
        default=False,
    )


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def _prepare_order_line_invoice_line(self, line, account_id=False):
        res = super(SaleOrderLine, self)._prepare_order_line_invoice_line(
            line, account_id
        )
        if line.is_delivery:
            res.update({'is_delivery': True})
        return res
