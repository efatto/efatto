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
from openerp import fields, models, api


class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    sale_journal_id = fields.Many2one(
        'account.journal', 'Default Sale Journal')
    purchase_journal_id = fields.Many2one(
        'account.journal', 'Default Purchase Journal')


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.onchange('fiscal_position')
    def change_journal(self):
        if self.type in ['out_invoice']:
            self.journal_id = self.fiscal_position.sale_journal_id or False
        elif self.type in ['in_invoice']:
            self.journal_id = self.fiscal_position.purchase_journal_id or False
