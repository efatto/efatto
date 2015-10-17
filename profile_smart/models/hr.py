# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 SimplERP srl (<http://www.simplerp.it>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields


class hr_expense_expense(models.Model):
    _inherit = 'hr.expense.expense'

    def action_move_create(self, cr, uid, ids, context=None):
        super(hr_expense_expense, self).action_move_create(cr, uid, ids, context=context)
        '''
        extend function that creates accounting entries when there is a partner in row, or date maturity
        '''
        move_obj = self.pool.get('account.move')
        for exp in self.browse(cr, uid, ids, context=context):
            move_id = exp.account_move_id.id
            separate_row = False
            for exp_line in exp.line_ids:
                if exp_line.partner_id or exp_line.date_maturity:
                    #  If filled partner or maturity, create one move for each partner
                    separate_row = True
            if separate_row:
                move_obj.write(cr, uid, [move_id], {'state': 'draft'})
                for move_line in exp.account_move_id.line_id:
                    move_line.unlink()
                company_currency = exp.company_id.currency_id.id
                diff_currency_p = exp.currency_id.id != company_currency
                # one account.move.line per expense line (+taxes..)
                eml = self.move_line_get(cr, uid, exp.id, context=context)

                # create a line for every counterpart
                for exp_line in exp.line_ids:
                    if exp_line.partner_id:
                        acc = exp_line.partner_id.property_account_payable.id
                    else:
                        acc = exp.employee_id.address_home_id.property_account_payable.id
                    eml.append({
                        'type': 'dest',
                        'name': '/',
                        'price': - exp_line.total_amount,
                        'account_id': acc,
                        'date_maturity': exp_line.date_maturity or exp.date_confirm,
                        'amount_currency': False,  # diff_currency_p and total_currency or False,
                        'currency_id': diff_currency_p and exp.currency_id.id or False,
                        'ref': exp.name,
                        'partner_id': exp_line.partner_id or exp.employee_id.address_home_id
                    })

                #  convert eml into an osv-valid format
                lines = map(lambda x: (0, 0, self.line_get_convert(
                    cr, uid, x, x.get('partner_id', exp.employee_id.address_home_id), exp.date_confirm, context=context)), eml)
                journal_id = move_obj.browse(cr, uid, move_id, context).journal_id
                # post the journal entry if 'Skip 'Draft' State for Manual Entries' is checked
                if journal_id.entry_posted:
                    move_obj.button_validate(cr, uid, [move_id], context)
                move_obj.write(cr, uid, [move_id], {'line_id': lines}, context=context)
                self.write(cr, uid, ids, {'account_move_id': move_id, 'state': 'done'}, context=context)
        return True


class hr_expense_line(models.Model):
    _inherit = "hr.expense.line"

    partner_id = fields.Many2one(
        'res.partner',
        domain="[('supplier', '=', True)]"
        'Supplier')
    date_maturity = fields.Date(
        'Maturity date')
