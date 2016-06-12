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

from openerp import models, fields, api, _


class project(models.Model):
    _inherit = "project.project"

    _defaults = {
        'use_tasks': True,
        'use_timesheets': True,
    }


class account_analytic_account(models.Model):
    _inherit = "account.analytic.account"

    def _get_100_percent(self, cr, uid, context):
        data_obj = self.pool.get('ir.model.data')
        data_id = data_obj._get_id(cr, uid, 'hr_timesheet_invoice', 'timesheet_invoice_factor1')
        if data_id:
            return data_obj.browse(cr, uid, data_id).res_id
        return False

    def project_create(self, cr, uid, analytic_account_id, vals, context=None):
        vals['use_tasks'] = True
        project_id = super(account_analytic_account, self).project_create(
            cr, uid, analytic_account_id, vals, context=context)
        project_obj = self.pool['project.project']
        project = project_obj.browse(cr, uid, [project_id], context=context)
        partner_obj = self.pool['res.partner']
        analytic_obj = self.pool['account.analytic.account']
        if project_id and vals.get('alias_mail', False):
            project_obj.write(cr, uid, [project_id], {
                'alias_name': vals.get('alias_mail')}, context=context)
            email = project.alias_id.name_get()[0][1]
            partner_id = partner_obj.search(
                cr, uid, [('email', '=', email)], context=context)
            if not partner_id:
                partner_id = partner_obj.create(cr, uid, {
                    'name': email, 'email': email, 'customer': False
                    }, context=context)
            pricelist = partner_obj.read(cr, uid, partner_id, ['property_product_pricelist'], context=context)
            pricelist_id = pricelist.get('property_product_pricelist', False) and pricelist.get(
                'property_product_pricelist')[0] or False
            if not analytic_obj.browse(cr, uid, analytic_account_id, context).pricelist_id:
                analytic_obj.write(cr, uid, analytic_account_id, {'pricelist_id': pricelist_id}, context=context)
            return project_id
        elif not project_id and vals.get('partner_id', False):
            pricelist = partner_obj.read(cr, uid, vals['partner_id'], ['property_product_pricelist'], context=context)
            pricelist_id = pricelist.get('property_product_pricelist', False) and pricelist.get(
                'property_product_pricelist')[0] or False
            analytic_obj = self.pool['account.analytic.account']
            if not analytic_obj.browse(cr, uid, analytic_account_id, context).pricelist_id:
                analytic_obj.write(cr, uid, analytic_account_id, {'pricelist_id': pricelist_id}, context=context)
            return project_id
        return False

    @api.one
    def _get_alias(self):
        for r in self:
            project = self.env['project.project'].search(
                [('analytic_account_id', 'in', [r.id])])
            if project:
                r.alias_id = project.alias_id.id

    alias_mail = fields.Char(
        'Alias', size=64,
        help="To be filled with text prior to @ to create an internal email "
        "associated with this project. Incoming emails are automatically "
        "synchronized with Tasks.")
    alias_id = fields.Many2one(
        'mail.alias',
        compute='_get_alias',
        string='Alias',
        help="Internal email associated with this project. Incoming emails are"
        " automatically synchronized with Tasks (or optionally Issues if the "
        "Issue Tracker module is installed).")
    _defaults = {
        'use_tasks': True,
        'use_timesheets': True,
        'to_invoice': _get_100_percent,
    }
