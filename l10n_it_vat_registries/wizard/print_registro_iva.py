# -*- encoding: utf-8 -*-
#
#
#    Copyright (C) 2011 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>).
#    Copyright (C) 2014 Agile Business Group sagl
#    (<http://www.agilebg.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

from openerp import models, fields, api, _
from openerp.exceptions import Warning


class wizard_registro_iva(models.TransientModel):

    @api.model
    def _get_period(self):
        ctx = dict(self._context or {}, account_period_prefer_normal=True)
        period_ids = self.env[
            'account.period'].with_context(context=ctx).find()
        return period_ids

    _name = "wizard.registro.iva"
    _rec_name = "type"

    period_ids = fields.Many2many(
        'account.period',
        'registro_iva_periods_rel',
        'period_id',
        'registro_id',
        string='Periods',
        default=_get_period,
        help='Select periods you want retrieve documents from',
        required=True)
    type = fields.Selection([
        ('customer', 'Customer Invoices'),
        ('supplier', 'Supplier Invoices'),
        ('corrispettivi', 'Corrispettivi'),
        ], 'Layout', required=True,
        default='customer')
    journal_ids = fields.Many2many(
        'account.journal',
        'registro_iva_journals_rel',
        'journal_id',
        'registro_id',
        string='Journals',
        help='Select journals you want retrieve documents from',
        required=True)
    tax_sign = fields.Float(
        string='Tax amount sign',
        default=1.0,
        help="Use -1 you have negative tax \
        amounts and you want to print them prositive")
    message = fields.Char(string='Message', size=64, readonly=True)
    fiscal_page_base = fields.Integer(
        string='Last printed page',
        required=True,
        default=0)

    def print_registro(self, cr, uid, ids, context=None):
        wizard = self.browse(cr, uid, ids[0], context=context)
        move_obj = self.pool['account.move']
        move_ids = move_obj.search(cr, uid, [
            ('journal_id', 'in', [j.id for j in wizard.journal_ids]),
            ('period_id', 'in', [p.id for p in wizard.period_ids]),
            ('state', '=', 'posted'),
            ], order='date, name')
        if not move_ids:
            raise Warning(_('No documents found in the current selection'))
        datas = {}
        datas_form = {}
        datas_form['fiscal_page_base'] = wizard.fiscal_page_base
        datas_form['period_ids'] = [p.id for p in wizard.period_ids]
        datas_form['tax_sign'] = wizard.tax_sign
        datas_form['registry_type'] = wizard.type
        report_name = 'l10n_it_vat_registries.report_registro_iva'
        datas = {
            'ids': move_ids,
            'model': 'account.move',
            'form': datas_form
        }
        return self.pool['report'].get_action(
            cr, uid, [], report_name, data=datas, context=context)

    @api.model
    def _get_journal(self, j_type):
        journal_obj = self.pool['account.journal']
        res = []
        if j_type == 'supplier':
            res = journal_obj.search(self.env.cr, self.env.uid, [('type', 'in', ['purchase', 'purchase_refund'])])
        elif j_type == 'customer' or j_type == 'corrispettivi':
            res = journal_obj.search(self.env.cr, self.env.uid, [('type', 'in', ['sale', 'sale_refund'])])
        else:
            res = journal_obj.search(self.env.cr, self.env.uid, [('type', 'in', ['sale', 'sale_refund', 'purchase', 'purchase_refund'])])
        return res

    @api.onchange('type')
    def on_type_changed(self):
        if self.type:
            if self.type == 'supplier':
                self.tax_sign = -1
            else:
                self.tax_sign = 1
            self.journal_ids = self._get_journal(self.type)
