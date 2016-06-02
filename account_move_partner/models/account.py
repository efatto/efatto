# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def onchange_partner_id(self, type, partner_id, date_invoice=False,
                            payment_term=False, partner_bank_id=False,
                            company_id=False):
        res = super(AccountInvoice, self).onchange_partner_id(
            type, partner_id, date_invoice=date_invoice,
            payment_term=payment_term, partner_bank_id=partner_bank_id,
            company_id=company_id)
        if not partner_id:
            return res
        lines = []
        account_ids = []
        partner = self.env['res.partner'].browse(partner_id)
        if type in ['out_invoice', 'out_refund']:
            account_ids = partner.sale_account_ids
        if type in ['in_invoice', 'in_refund']:
            account_ids = partner.purchase_account_ids
        for line in account_ids:
            lines.append({
                'name': line.name,
                'account_id': line.id,
                'invoice_line_tax_id': line.tax_ids,
                'quantity': 1,
                'price_unit': 1,
            })
        if lines:
            res['value'].update({'invoice_line': lines})
        return res
