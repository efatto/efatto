# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

import time

from openerp.osv import fields, osv
from openerp.tools.translate import _

import logging
_logger = logging.getLogger(__name__)

class stock_move(osv.Model):
	_inherit = "stock.move"
	_table = "stock_move"
	_order = "name desc"

	_columns = {
		'product_container_id': fields.related('product_id','container_id',string='Package',type='many2one',relation='product.product',store=True, readonly=True),
	}     
        
	def action_done(self, cr, uid, ids, context=None):
		_logger.debug("Executing stock.move.action_done");
		if context is None:
			context = {}
            
		donemove = []
		for move in self.browse(cr, uid, ids, context=context):
			if move.state=="done":
				_logger.debug("stock_move.action_done: move id %s already done",move.id)
				donemove.append(move.id)
				
		res = super(stock_move, self).action_done(cr, uid, ids, context=context)
		move_pool = self.pool.get('stock.move')
		
		for move_id in ids:
			if move_id in donemove:
				_logger.debug("stock_move.action_done: bypassing move id %s",move.id)
				continue
			move = self.browse(cr, uid, move_id)
			if move.product_id.container_id:
				_logger.debug('stock_move.action_done: moving container id for product %s',move.product_id)
				res = {
					'product_id':move.product_id.container_id.id,
					'product_qty':move.product_qty,
					'product_uom':move.product_id.container_id.uom_id.id,
					'name':move.name,
					'origin':move.picking_id.name,
					'type':'internal',
					'location_id':move.location_id.id,
					'location_dest_id':move.location_dest_id.id,
					'partner_id':move.partner_id.id,
					'date':move.date,
					'state':'done'
				}
				move_pool.create(cr, uid, res)
			elif move.product_id.product_tmpl_id.container_id:
				_logger.debug('stock_move.action_done: moving container id from template for product %s',move.product_id)
				res = {
					'product_id':move.product_id.product_tmpl_id.container_id.id,
					'product_qty':move.product_qty,
					'product_uom':move.product_id.product_tmpl_id.container_id.uom_id.id,
					'name':move.name,
					'origin':move.picking_id.name,
					'type':'internal',
					'location_id':move.location_id.id,
					'location_dest_id':move.location_dest_id.id,
					'partner_id':move.partner_id.id,
					'date':move.date,
					'state':'done'
				}
				move_pool.create(cr, uid, res)
		_logger.debug("Finished processing stock.move.action_done");
		return True
    
stock_move()
