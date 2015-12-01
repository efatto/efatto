# -*- coding: utf-8 -*-
#
#
#    Copyright (C) 2015 SimplERP srl (<http://www.simplerp.it>).
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
from openerp import api, fields, models
from openerp.tools.translate import _

PAYMENT_TERM_TYPE_SELECTION = [
    ('BB', 'Bonifico Bancario'),
    ('BP', 'Bonifico Postale'),
    ('RD', 'Rimessa Diretta'),
    ('RB', 'Ricevuta Bancaria'),
    ('F4', 'F24'),
    ('PP', 'Paypal'),
    ('CC', 'Carta di Credito'),
    ('CO', 'Contrassegno'),
    ('CN', 'Contanti'),
    ('SD', 'Sepa DD'),
]


class account_payment_term_line(models.Model):
    _inherit = 'account.payment.term.line'

    type = fields.Selection(
        PAYMENT_TERM_TYPE_SELECTION, "Type of payment")


class account_move_line(models.Model):
    _inherit = 'account.move.line'

    payment_term_type = fields.Selection(
        PAYMENT_TERM_TYPE_SELECTION, 'Payment line term type')


class account_invoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        super(account_invoice, self).finalize_invoice_move_lines(move_lines)
        totlines = False
        amount = 0
        for line in move_lines:
            if line[2].get('date_maturity', False):
                amount += (line[2]['credit'] > 0 and line[2]['credit'] or \
                           line[2]['debit'])
        if self.payment_term:
            totlines = self.payment_term.compute(amount, self.date_invoice or False)[0]
        for line in move_lines:
            if totlines:
                for pay_line in totlines:
                    if line[2].get('date_maturity', False) == pay_line[0] and \
                            (line[2]['credit'] == pay_line[1] or
                             line[2]['debit'] == pay_line[1]):
                        line[2].update({'payment_term_type': pay_line[2]})
                        totlines.remove(pay_line)
        return move_lines
