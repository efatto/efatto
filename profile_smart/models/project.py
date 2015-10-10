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

    _defaults = {
        'use_tasks': True,
        'use_timesheets': True,
        'to_invoice': _get_100_percent,
    }


class hr_expense_line(models.Model):
    _inherit = "hr.expense.line"

    partner_id = fields.Many2one(
        'res.partner',
        domain="[('supplier', '=', True)]"
        'Supplier')
    date_maturity = fields.Date(
        'Maturity date')
