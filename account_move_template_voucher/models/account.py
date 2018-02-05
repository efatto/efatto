# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, exceptions, _


class AccountVoucher(models.Model):
    _inherit = "account.voucher"

    template_id = fields.Many2one(
        'account.move.template', 'Account Move Template',
        domain=[('journal_id.type', 'in', ['cash','bank'])]
    )

    @api.onchange('template_id')
    def onchange_template_id(self):
        if not self.template_id:
            return
        if self.template_id.cross_journals:
            raise exceptions.Warning(_("Error! Not possible in more than one "
                                       "journal. Create from wizard"))
        if self.template_id.journal_id:
            self.journal_id = self.template_id.journal_id
        elif self.template_id.template_line_ids:
            if self.template_id.template_line_ids[0].journal_id:
                self.journal_id = self.template_id.template_line_ids[
                    0].journal_id

    @api.model
    def account_move_get(self, voucher_id):
        move = super(AccountVoucher, self).account_move_get(
            voucher_id=voucher_id)
        if voucher_id:
            voucher = self.browse(voucher_id)
            if voucher.template_id:
                move['template_id'] = voucher.template_id.id
        return move

    @api.multi
    def onchange_amount(self, amount, rate, partner_id, journal_id,
                        currency_id, ttype, date, payment_rate_currency_id,
                        company_id):
        if self.env['ir.config_parameter'].get_param(
                    'account.voucher.disable.onchange.amount'):
            return False
        return super(AccountVoucher, self).onchange_amount(
            amount, rate, partner_id, journal_id, currency_id, ttype, date,
            payment_rate_currency_id, company_id)
