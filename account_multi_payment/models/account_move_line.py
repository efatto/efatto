# -*- encoding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2015 Didotech SRL
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
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields


class account_move_line(orm.Model):
    _inherit = 'account.move.line'

    _columns = {
        'user_type': fields.related(
                'account_id', 'user_type', type='many2one', relation='account.account', string='Account user type', store=False),
        'date_from':fields.function(lambda *a,**k:{}, method=True, type='date',string="Date from"),
        'date_to':fields.function(lambda *a,**k:{}, method=True, type='date',string="Date to"),
    }


class account_journal(orm.Model):
    _inherit = 'account.journal'
    _order = 'name'
