# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Didotech srl
#    (<http://www.didotech.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
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
##############################################################################

from openerp import models, fields, api, _
from openerp.exceptions import Warning


class account_tax(models.Model):
    _inherit = 'account.tax'

    @api.multi
    @api.depends('tax_id', 'defaults')
    def copy(self):
        raise Warning(_("Tax can't be duplicated"))
        return False

    @api.model
    def create(self, vals):

        tax_code_obj = self.env['account.tax.code']
        if self.search([('name', '=', vals['name'])]):
            raise Warning(_("Tax name must be unique."))
        if vals.get('description', False):
            if self.search([('description', '=', vals['description'])]):
                raise Warning(_("Tax description must be unique."))
        if vals['type_tax_use'] == 'sale':
            vals.update({'base_sign': 1, 'tax_sign': 1, 'ref_base_sign': -1, 'ref_tax_sign': -1})
        elif vals['type_tax_use'] == 'purchase':
            vals.update({'base_sign': -1, 'tax_sign': -1, 'ref_base_sign': 1, 'ref_tax_sign': 1})

        if vals.get('base_code_id', False) and vals.get('tax_code_id', False):
            return super(account_tax, self).create(vals)

        if not vals.get('base_code_id', False) and vals.get('account_base_tax_code_id', False):
            parent_base_tax_code = tax_code_obj.browse(vals['account_base_tax_code_id'])
            base_tax_code_vals = {
                'name': vals['name'] + ' (imp)',
                'code': parent_base_tax_code.code + vals['description'],
                'parent_id': vals['account_base_tax_code_id'],
                'is_base': True,
                'vat_statement_type': vals['type_tax_use'] == 'sale' and 'debit' or vals['type_tax_use'] == 'purchase' and 'credit',
                'vat_statement_sign': vals['type_tax_use'] == 'sale' and 1 or vals['type_tax_use'] == 'purchase' and -1,
            }
            i = 0
            name = vals['name'] + ' (imp)'
            while True:
                if tax_code_obj.search([('name', '=', name)]):
                    name += str(i)
                    i += 1
                else:
                    if i > 0:
                        base_tax_code_vals['name'] += str(i)
                    break
            base_code = tax_code_obj.create(base_tax_code_vals)
            vals.update({'base_code_id': base_code.id})

        if not vals.get('tax_code_id', False) and vals.get('account_tax_code_id', False):
            parent_tax_code = tax_code_obj.browse(vals['account_tax_code_id'])
            tax_code_vals = {
                'name': vals['name'],
                'code': parent_tax_code.code + vals['description'],
                'parent_id': vals['account_tax_code_id'],
                'is_base': False,
                'vat_statement_type': vals['type_tax_use'] == 'sale' and 'debit' or vals['type_tax_use'] == 'purchase' and 'credit',
                'vat_statement_sign': vals['type_tax_use'] == 'sale' and 1 or vals['type_tax_use'] == 'purchase' and -1,
            }
            i = 0
            name = vals['name']
            while True:
                if tax_code_obj.search([('name', '=', name)]):
                    name += str(i)
                    i += 1
                else:
                    if i > 0:
                        tax_code_vals['name'] += str(i)
                    break
            tax_code = tax_code_obj.create(tax_code_vals)
            vals.update({'tax_code_id': tax_code.id})

        return super(account_tax, self).create(vals)

    @api.multi
    def write(self, vals):
        tax_code_obj = self.pool['account.tax.code']
        tax = self[0]
        if vals.get('name', False):
            if self.search([('name', '=', vals['name'])]):
                raise Warning(_("Tax name must be unique."))
        if vals.get('description', False):
            if self.search([('description', '=', vals['description'])]):
                raise Warning(_("Tax description must be unique."))
        if vals.get('type_tax_use', False):
            if vals['type_tax_use'] != tax.type_tax_use:
                raise Warning(_("Tax Type cannot be changed - create a different tax."))
        if (vals.get('type_tax_use', False) or tax.type_tax_use) == 'sale':
            vals.update({'base_sign': 1, 'tax_sign': 1, 'ref_base_sign': -1, 'ref_tax_sign': -1})
        elif (vals.get('type_tax_use', False) or tax.type_tax_use) == 'purchase':
            vals.update({'base_sign': -1, 'tax_sign': -1, 'ref_base_sign': 1, 'ref_tax_sign': 1})
        if tax.base_code_id or tax.tax_code_id:
            return super(account_tax, self).write(vals)
        if not tax.base_code_id:
            if not vals.get('account_base_tax_code_id', False) and not tax.account_base_tax_code_id:
                raise Warning(_("Base Tax Code parent must be set."))
            elif not vals.get('base_code_id', False):
                parent_base_tax_code = tax.account_base_tax_code_id or tax_code_obj.browse(vals['account_base_tax_code_id'])
                base_tax_code_vals = {
                    'name': tax.name or vals.get('name') + ' (imp)',
                    'code': parent_base_tax_code.code + tax.description or vals.get('description'),
                    'parent_id': tax.account_base_tax_code_id.id or vals.get('account_base_tax_code_id'),
                    'is_base': True,
                    'vat_statement_type': (tax.type_tax_use or vals.get('type_tax_use')) == 'sale' and 'debit' or (tax.type_tax_use or vals.get('type_tax_use')) == 'purchase' and 'credit',
                    'vat_statement_sign': (tax.type_tax_use or vals.get('type_tax_use')) == 'sale' and 1 or (tax.type_tax_use or vals.get('type_tax_use')) == 'purchase' and -1,
                }
                base_code = tax_code_obj.create(base_tax_code_vals)
                vals.update({'base_code_id': base_code.id})

        if not tax.tax_code_id:
            if not vals.get('account_tax_code_id', False) and not tax.account_tax_code_id:
                raise Warning(_("Tax Code parent must be set."))
            elif not vals.get('tax_code_id', False):
                parent_tax_code = tax.account_tax_code_id or tax_code_obj.browse(vals['account_tax_code_id'])
                tax_code_vals = {
                    'name': tax.name or vals.get('name'),
                    'code': parent_tax_code.code + tax.description or vals.get('description'),
                    'parent_id': tax.account_tax_code_id.id or vals.get('account_tax_code_id'),
                    'is_base': False,
                    'vat_statement_type': (tax.type_tax_use or vals.get('type_tax_use')) == 'sale' and 'debit' or (tax.type_tax_use or vals.get('type_tax_use')) == 'purchase' and 'credit',
                    'vat_statement_sign': (tax.type_tax_use or vals.get('type_tax_use')) == 'sale' and 1 or (tax.type_tax_use or vals.get('type_tax_use')) == 'purchase' and -1,
                }
                tax_code = tax_code_obj.create(tax_code_vals)
                vals.update({'tax_code_id': tax_code.id})

        return super(account_tax, self).write(vals)

    @api.multi
    def onchange_tax_sign(self, type_tax_use):
        if type_tax_use:
            if type_tax_use == "sale":
                return {'value': {'base_sign': 1, 'tax_sign': 1, 'ref_base_sign': -1, 'ref_tax_sign': -1}}
            elif type_tax_use == "purchase":
                return {'value': {'base_sign': -1, 'tax_sign': -1, 'ref_base_sign': 1, 'ref_tax_sign': 1}}
            elif type_tax_use == "all":
                return {'value': {'base_sign': 1, 'tax_sign': 1, 'ref_base_sign': 1, 'ref_tax_sign': 1}}

    account_tax_code_id = fields.Many2one(
        'account.tax.code', string='Tax Code Parent',
        required=False, help='Parent tax code')
    account_base_tax_code_id = fields.Many2one(
        'account.tax.code', string='Base Tax Code Parent',
        required=False, help='Parent base tax code')
    account_collected_id = fields.Many2one(
        'account.account', string='Invoice Tax Account',
        related='account_tax_code_id.vat_statement_account_id', copy=False, readonly=True)
    account_paid_id = fields.Many2one(
        'account.account', string='Refund Tax Account',
        related='account_tax_code_id.vat_statement_account_id', copy=False, readonly=True)
