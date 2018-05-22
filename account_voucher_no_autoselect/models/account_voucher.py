# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, fields, exceptions, _


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    @api.multi
    def recompute_voucher_lines(self, partner_id, journal_id, price,
                                currency_id, ttype, date):
        res = super(AccountVoucher, self).recompute_voucher_lines(
            partner_id, journal_id, price, currency_id, ttype, date
        )
        for line in res['value']['line_cr_ids']:
            if 'reconcile' in line:
                line['reconcile'] = False
            if 'amount' in line and line.get('amount', False) != 0.0:
                line['amount'] = 0.0
        for line in res['value']['line_dr_ids']:
            if 'reconcile' in line:
                line['reconcile'] = False
            if 'amount' in line and line.get('amount', False) != 0.0:
                line['amount'] = 0.0
        return res
