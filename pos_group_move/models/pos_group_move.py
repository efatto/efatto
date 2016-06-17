# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp.osv import fields, osv


class pos_order(osv.Model):
    _inherit = 'pos.order'

    def _create_account_move_line(self, cr, uid, ids, session=None,
                                  move_id=None, context=None):
        result = super(pos_order, self)._create_account_move_line(
            cr, uid, ids, session=session, move_id=move_id, context=context)
        if not context:
            context = {}
        # for move in self.browse(cr, uid, [result], context):
        #     moves = move.picking_id.move_lines
        #     self.pool['stock.move']._create_procurements(cr, uid, moves, context=context)
        return result
