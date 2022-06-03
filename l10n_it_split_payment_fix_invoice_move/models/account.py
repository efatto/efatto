# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, _
from openerp.exceptions import Warning as UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _build_debit_line(self):
        vals = super(AccountInvoice, self)._build_debit_line()
        # add tax code and negative value if out, positive if refund
        move_lines = self.move_id.line_id.filtered(
            lambda x: not x.tax_code_id.is_base)
        tax_code_id = move_lines.mapped('tax_code_id')
        if len(tax_code_id) == 1:
            vals['tax_code_id'] = tax_code_id.id
        if len(tax_code_id) > 1:
            raise UserError(_('Invoice with Split payment with more than 1 '
                            'taxes is not valid!'))
        vals['tax_amount'] = self.amount_sp * (
            -1 if self.type == 'out_invoice' else 1)
        return vals
