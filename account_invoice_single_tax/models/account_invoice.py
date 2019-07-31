# -*- coding: utf-8 -*-

from openerp import models, api, exceptions, _


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def single_invoice_line_tax(self):
        errors = []
        for invoice in self:
            for invoice_line in invoice.invoice_line:
                if len(invoice_line.invoice_line_tax_id) > 1:
                    error_string = "%s \n" % invoice_line.name
                    errors.append(error_string)
        if errors:
            errors_full_string = ','.join(x for x in errors)
            raise exceptions.Warning(
                _('Multiple Taxes Defined in lines:'), errors_full_string)
        else:
            return True

    @api.multi
    def invoice_validate(self):
        self.single_invoice_line_tax()
        res = super(AccountInvoice, self).invoice_validate()
        return res
