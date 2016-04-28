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
        if not any(picking.ddt_ids for picking in (
                move.picking_id for move in self.browse(
                cr, uid, ids, context))) and \
                not (self.location_dest_id.usage == 'internal' or
                     self.location_dest_id.usage == 'production'):
            raise Warning(_('This transfer is not linked to a ddt!'))
            return False
        return super(StockMove, self).action_done(cr, uid, ids, context)
        #todo update view of ddt_ids (on back of current view)