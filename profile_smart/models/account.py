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
from openerp import models, fields, api


class AccountJournal(models.Model):
    _inherit = "account.journal"

    generic_expense = fields.Boolean(
            string='Generic Expense type'
    )
    default_partner_id = fields.Many2one(
        'res.partner',
        string="Default partner",
        help="Used for expenses without VAT statement",
    )

    _defaults = {
        'update_posted': True,
    }


class account_invoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def onchange_journal_id(self, journal_id=False):
        res = super(account_invoice, self).onchange_journal_id(journal_id=journal_id)
        if journal_id:
            journal = self.env['account.journal'].browse(journal_id)
            if journal.generic_expense and journal.default_partner_id:
                res['value'].update({
                    'partner_id': journal.default_partner_id.id,
                })
        return res

#TODO if account_id.type not in ['payable','receivable'] trg wkfl paied

    expense_generic = fields.Boolean(
        string='Expense generic',
        related='journal_id.generic_expense',
        store=True, readonly=True
    )
