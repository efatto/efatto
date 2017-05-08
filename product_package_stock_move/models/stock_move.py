# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, fields


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.multi
    def action_done(self):
        res = super(StockMove, self).action_done()
        for move in self.filtered(lambda x: x.state == 'done'):
            if move.product_id.product_pack_id:
                values = {
                    'product_id': move.product_id.product_pack_id.id,
                    'product_uom_qty': move.product_qty,
                    'product_uom': move.product_id.product_pack_id.uom_id.id,
                    'name': move.product_id.product_pack_id.name,
                    'origin': move.picking_id.name,
                    'type': 'internal',
                    'location_id': move.location_id.id,
                    'location_dest_id': move.location_dest_id.id,
                    'partner_id': move.partner_id.id,
                    'date': move.date,
                    'state': 'done',
                    'picking_id': move.picking_id.id,
                    # non era collegato al picking prima, problemi?
                }
                self.env['stock.move'].create(values)
        return res
