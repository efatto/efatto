# -*- coding: utf-8 -*-

from openerp import models, api, exceptions, _


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.constrains('invoice_line_tax_id')
    def _check_single_invoice_line_tax(self):
        for invoice_line in self:
            if len(invoice_line.invoice_line_tax_id) > 1:
                raise exceptions.Warning(
                    _('Multiple Taxes Defined in line %s') % invoice_line.name)
