# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright Camptocamp SA 2011
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

from openerp.osv import fields, orm


class AccountPartnerInvoicedWizard(orm.TransientModel):
    """Will launch partner balance report and pass required args"""

    _inherit = "account.common.balance.report"
    _name = "partner.invoiced.webkit"
    _description = "Partner Invoiced Report"

    def _journal_invoice(self, cr, uid, context=None):
        return self.pool['account.journal'].search(cr, uid, [(
         'type', 'in', [
             'sale', 'sale_refund', 'purchase', 'purchase_refund'])])

    def onchange_account_view_selection(self, cursor, uid, ids,
                                  account_view_selection=False,
                                  context=None):
        res = {'value': {}}
        domain = [account_view_selection, ]
        if account_view_selection == 'payable_receivable':
            domain = ['payable', 'receivable']

        res['value']['account_ids'] = self.pool['account.account'].search(
            cursor, uid, [('type', 'in', domain)], context=context)
        return res

    _columns = {
        'account_view_selection': fields.selection([
            ('receivable','Customer'),
            ('payable','Supplier'),
            ('payable_receivable','Customer and Supplier'),
        ], "Account type"),
        'partner_ids': fields.many2many(
            'res.partner', string='Filter on partner',
            help="Only selected partners will be printed. Leave empty to "
                 "print all partners."),
        'journal_ids': fields.many2many('account.journal',
                                        'account_invoiced_report_journal_rel',
                                        'account_id', 'journal_id', 'Journals',
                                        required=True),
        'display_only_total': fields.boolean('Display only total'),
    }

    _defaults = {
        'journal_ids': _journal_invoice,
        'display_only_total': True,
    }

    def pre_print_report(self, cr, uid, ids, data, context=None):
        data = super(AccountPartnerInvoicedWizard, self).pre_print_report(
            cr, uid, ids, data, context)
        if context is None:
            context = {}
        vals = self.read(cr, uid, ids,
                         ['account_view_selection', 'account_ids',
                          'display_only_total'],
                         context=context)[0]
        data['form'].update(vals)
        return data

    def _print_report(self, cursor, uid, ids, data, context=None):
        context = context or {}
        # we update form with display account value
        data = self.pre_print_report(cursor, uid, ids, data, context=context)

        return {'type': 'ir.actions.report.xml',
                'report_name':
                    'account.account_report_partner_invoiced_webkit',
                'datas': data}
