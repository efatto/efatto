# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _get_amount_residual_signed(self):
        for move in self:
            move.amount_residual_signed = (
                move.amount_residual if move.debit != 0.0
                else move.amount_residual * -1)

    abi = fields.Char(
            related='partner_id.bank_riba_id.abi', string='ABI',
            store=False)
    cab = fields.Char(
            related='partner_id.bank_riba_id.cab', string='CAB',
            store=False)
    amount_residual_signed = fields.Float(
        compute=_get_amount_residual_signed,
        string='Amount Residual Signed')
