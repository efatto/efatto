# -*- coding: utf-8 -*-
#
#
#    Copyright (C) 2016 Sergio Corato - SimplERP srl (<http://www.simplerp.it>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
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

    _order = 'date_cashflow, id'


class AccountMove(models.Model):
    _inherit = "account.move"

    is_cashflow = fields.Boolean('Cashflow temporary line')
