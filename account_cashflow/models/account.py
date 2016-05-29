# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.one
    @api.depends('date', 'date_maturity')
    def _get_date_cashflow(self):
        if self.date_maturity:
            self.date_cashflow = self.date_maturity
        elif self.date:
            self.date_cashflow = self.date

    @api.multi
    @api.depends('date_cashflow')
    def _balance_cashflow(self):
        total = 0
        for record in self.sorted(key=lambda t: t.date_cashflow):
            if record.account_id.type in [
                    'payable', 'receivable'] and not record.date_maturity:
                continue
            else:
                record.balance_cashflow = (
                    record.maturity_residual and record.maturity_residual or
                    record.debit - record.credit) + total
                total = record.balance_cashflow

    balance_cashflow = fields.Float(
        compute='_balance_cashflow', string='Balance Cashflow')
    is_cashflow = fields.Boolean('Cashflow temporary line')
    date_cashflow = fields.Date(
        compute='_get_date_cashflow', store=True, string='Date cashflow')
    account_short_name = fields.Char(
        related='account_id.name', string="Account", size=30)
    journal_short_name = fields.Char(
        related='journal_id.name', string="Journal", size=30)

    _order = 'date_cashflow, id'


class AccountMove(models.Model):
    _inherit = "account.move"

    is_cashflow = fields.Boolean('Cashflow temporary line')
