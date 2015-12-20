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

from openerp import models, fields


class AccountConfigSettings(models.TransientModel):

    _inherit = 'account.config.settings'

    accountant_partner_id = fields.Many2one(
        related='company_id.accountant_partner_id',
        help='Default Accountant partner',
        domain=[('supplier', '=', True)])

    def default_get(self, cr, uid, fields, context=None):
        res = super(AccountConfigSettings, self).default_get(
            cr, uid, fields, context)
        if res:
            user = self.pool['res.users'].browse(cr, uid, uid, context)
            res['due_cost_service_id'] = user.company_id.accountant_partner_id.id
        return res


class ResCompany(models.Model):

    _inherit = 'res.company'

    accountant_partner_id = fields.Many2one('res.partner')
