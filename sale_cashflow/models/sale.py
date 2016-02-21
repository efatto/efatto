# -*- coding: utf-8 -*-
#
#
#    Copyright (C) 2016 Sergio Corato - SimplERP srl (<http://www.simplerp.it>).
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
from openerp import models, fields, api
from openerp.tools.float_utils import float_round, float_compare
from openerp.tools.translate import _

import openerp.addons.decimal_precision as dp
import math


class sale_order(models.Model):
    _inherit = 'sale.order'

    @api.one
    def create_move(self, order):
        move_obj = self.env['account.move']
        line_obj = self.env['account.move.line']
        period_obj = self.env['account.period']
        journal_id = order.partner_id.company_bank_id.journal_id.id
        period_ids = period_obj.find(dt=order.date_order)
        if len(period_ids) != 1:
            raise Warning(_(
                "No period found or more than one period found for the "
                "given date.")
            )
        move_data = {
            'name': _('Cash flow temporary move') + ' - ' + order.date_order,
            'date': order.date_order,
            'journal_id': journal_id,
            'period_id': period_ids[0].id,
        }
        order.cashflow_move_id = move_obj.create(move_data)
        totlines = order.payment_term.compute(
            order.amount_total, False)[0]
        if totlines:
            for pay_line in totlines:
                date_maturity = pay_line[0]
                amount = pay_line[1]
                if amount != 0.0:
                    line_data = {
                        'name': _('Cashflow move line'),
                        'account_id': order.partner_id.company_bank_id.journal_id.default_credit_account_id.id,
                        'move_id': order.cashflow_move_id.id,
                        'journal_id': journal_id,
                        'debit': amount > 0 and amount or 0.0,
                        'credit': amount < 0 and amount or 0.0,
                        'date_maturity': date_maturity,
                        'date': order.date_order,
                        'period_id': period_ids[0].id,
                        'is_cashflow': True,
                    }
                    line_obj.create(line_data)
            total_line_data = {
                'name': _('Cashflow total'),
                'account_id': order.partner_id.company_id.cashflow_account_id.id,
                'move_id': order.cashflow_move_id.id,
                'journal_id': journal_id,
                'debit': order.amount_total < 0 and order.amount_total or 0.0,
                'credit': order.amount_total > 0 and order.amount_total or 0.0,
                'date': order.date_order,
                'period_id': period_ids[0].id,
                'is_cashflow': True,
            }
            line_obj.create(total_line_data)

    @api.multi
    def action_button_confirm(self):
        res = super(sale_order, self).action_button_confirm()
        for order in self:
            if order.payment_term:
                self.create_move(order)
        return res

    cashflow_move_id = fields.Many2one(
        'account.move', 'Cashflow temporary moves')
