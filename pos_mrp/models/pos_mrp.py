# -*- coding: utf-8 -*-
#
#
#    Copyright (C) 2016 SimplERP srl (<http://www.simplerp.it>).
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
from openerp.osv import fields, osv


class pos_order(osv.Model):
    _inherit = 'pos.order'

    def _prepare_order_line_procurement(self, cr, uid, order, line, group_id=False, context=None):
        result = super(pos_order, self)._prepare_order_line_procurement(cr, uid, order, line, group_id=group_id, context=context)
        result['property_ids'] = [(6, 0, [x.id for x in line.property_ids])]
        return result

    def action_paid(self, cr, uid, ids, context=None):
        super(pos_order, self).action_paid(cr, uid, ids, context=context)
        if not context:
            context = {}
        for order in self.browse(cr, uid, ids, context):
            moves = order.picking_id.move_lines
            self.pool['stock.move']._create_procurements(cr, uid, moves, context=context)
        return True


class pos_order_line(osv.osv):

    _inherit = 'pos.order.line'
    _columns = {
        'property_ids': fields.many2many('mrp.property', 'pos_order_line_property_rel', 'order_id', 'property_id', 'Properties', readonly=True, states={'draft': [('readonly', False)]}),
    }
