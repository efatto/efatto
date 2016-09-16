# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import api, _, models
from openerp.exceptions import Warning


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.cr_uid_ids_context
    def do_enter_transfer_details(self, cr, uid, picking_ids, context=None):
        if not any(picking.ddt_ids for picking in self.browse(
                cr, uid, picking_ids, context)):
            raise Warning(_('This transfer is not linked to a ddt!'))
            return False
        res = super(StockPicking, self).do_enter_transfer_details(
            cr, uid, picking_ids, context=context)
        return res

    @api.cr_uid_ids_context
    def do_transfer(self, cr, uid, picking_ids, context=None):
        if not any(picking.ddt_ids for picking in self.browse(
                cr, uid, picking_ids, context)):
            raise Warning(_('This transfer is not linked to a ddt!'))
            return False
        res = super(StockPicking, self).do_transfer(
            cr, uid, picking_ids, context=context)
        if res:
            for ddt in self.browse(cr, uid, picking_ids, context).ddt_ids:
                ddt.set_done()
        return res


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.cr_uid_ids_context
    def action_done(self, cr, uid, ids, context=None):
        for move in self.browse(cr, uid, ids, context):
            if not any(picking.ddt_ids for picking in move.picking_id) and \
                not (move.picking_id.location_dest_id.usage == 'internal' or
                     move.picking_id.location_dest_id.usage == 'production'):
                raise Warning(_('This transfer is not linked to a ddt!'))
                return False
        return super(StockMove, self).action_done(cr, uid, ids, context)
        #todo update view of ddt_ids (on back of current view)