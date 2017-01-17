# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class ProcurementBatchGenerator(models.TransientModel):
    _inherit = 'procurement.batch.generator'

    @api.model
    def _default_lines(self):
        assert isinstance(self.env.context['active_ids'], list),\
            "context['active_ids'] must be a list"
        assert self.env.context['active_model'] == 'product.product',\
            "context['active_model'] must be 'product.product'"
        res = []
        warehouses = self.env['stock.warehouse'].search(
            [('company_id', '=', self.env.user.company_id.id)])
        warehouse_id = warehouses and warehouses[0].id or False
        today = fields.Date.context_today(self)
        for product in self.env['product.product'].browse(
                self.env.context['active_ids']):
            res.append({
                'product_id': product.id,
                'partner_id': product.seller_id.id or False,
                'qty_available': product.qty_available,
                'outgoing_qty': product.outgoing_qty,
                'incoming_qty': product.incoming_qty,
                'uom_id': product.uom_id.id,
                'procurement_qty': (product.qty_available
                                    - product.outgoing_qty
                                    + product.incoming_qty) < 0.0 and
                                    - (product.qty_available
                                    - product.outgoing_qty
                                    + product.incoming_qty) or 0.0,
                'warehouse_id': warehouse_id,
                'date_planned': today,
                })
        return res

    line_ids = fields.One2many(default=_default_lines)