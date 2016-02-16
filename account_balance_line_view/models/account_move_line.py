# -*- coding: utf-8 -*-
#
#
#    Copyright (C) 2016 Sergio Corato - SimplERP srl (<http://www.simplerp.it>).
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
from openerp.osv import osv, fields


class account_move_line(osv.osv):
    _inherit = "account.move.line"

    def _balance(self, cr, uid, ids, name, arg, context=None):
        super(account_move_line, self)._balance(
            cr, uid, ids, name, arg, context=context)
        if context is None:
            context = {}
        c = context.copy()
        c['initital_bal'] = True
        sql = """SELECT l1.id, COALESCE(SUM(l2.debit-l2.credit), 0)
                    FROM account_move_line l1 LEFT JOIN account_move_line l2
                    ON (l1.account_id = l2.account_id
                      AND (l2.date < l1.date
                      OR (l2.date = l1.date AND l2.id <= l1.id))
                      AND """ + \
                self._query_get(cr, uid, obj='l2', context=c) + \
                ") WHERE l1.id IN %s GROUP BY l1.id"

        cr.execute(sql, [tuple(ids)])
        return dict(cr.fetchall())

    def _balance_search(self, cursor, user, obj, name, args, domain=None, context=None):
        return super(account_move_line, self)._balance_search(
            cursor, user, obj, name, args, domain=domain, context=context)

    _columns = {
        'balance': fields.function(_balance, fnct_search=_balance_search, string='Balance'),
    }