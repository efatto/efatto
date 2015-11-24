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


class project(models.Model):
    _inherit = "project.project"

    _defaults = {
        'use_tasks': True,
        'use_timesheets': True,
    }


class account_analytic_account(models.Model):
    _inherit = "account.analytic.account"

    def _get_100_percent(self, cr, uid, context):
        ids = self.pool.get('hr_timesheet_invoice.factor').search(
            cr, uid, [('name', 'ilike', '100')], context=context)
        return ids[0]

    def project_create(self, cr, uid, analytic_account_id, vals, context=None):
        project = super(account_analytic_account, self).project_create(cr, uid, analytic_account_id, vals, context=context)
        project_pool = self.pool.get('project.project')
        if project and vals.get('alias_mail', False):
            project_pool.write(cr, uid, [project], {'alias_name': vals.get('alias_mail')}, context=context)
            return project
        elif project:
            return project
        return False

# TODO: project write

    @api.one
    def _get_alias(self):
        for r in self:
            project = self.env['project.project'].search([('analytic_account_id', 'in', [r.id])])
            if project:
                r.alias_id = project.alias_id.id

    alias_mail = fields.Char(
        'Alias', required=True, size=64,
        help="To be filled with text prior to @ to create an internal email associated with this project."
        " Incoming emails are automatically synchronized with Tasks.")
    alias_id = fields.Many2one(
        'mail.alias',
        compute='_get_alias',
        string='Alias',
        help="Internal email associated with this project. Incoming emails are automatically synchronized"
        "with Tasks (or optionally Issues if the Issue Tracker module is installed).")
    _defaults = {
        'use_tasks': True,
        'use_timesheets': True,
        'to_invoice': _get_100_percent,
    }
