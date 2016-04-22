# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
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
