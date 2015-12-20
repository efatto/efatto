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

from openerp.osv import fields, orm
from openerp import api, _, models
from openerp.exceptions import Warning as UserError


class AccountMoveLine(orm.Model):
    _inherit = "account.move.line"

    _columns = {
        'abi': fields.related(
            'partner_id', 'bank_riba_id', 'abi', type='char', string='ABI',
            store=False),
        'cab': fields.related(
            'partner_id', 'bank_riba_id', 'cab', type='char', string='CAB',
            store=False),

    }