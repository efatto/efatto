# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp.osv import osv


class delivery_grid(osv.osv):
    _inherit = "delivery.grid"

    def get_price(self, cr, uid, id, order, dt, context=None):
        total = weight = volume = quantity = 0
        product_uom_obj = self.pool.get('product.uom')
        for line in order.order_line:
            if line.state == 'cancel':
                continue
            if not line.is_delivery:
                total += line.price_subtotal
            if not line.product_id or line.is_delivery:
                continue
            q = product_uom_obj._compute_qty(
                cr, uid, line.product_uom.id, line.product_uom_qty,
                line.product_id.uom_id.id)
            weight += (line.product_id.weight or 0.0) * q
            volume += (line.product_id.volume or 0.0) * q
            quantity += q
        ctx = context.copy()
        ctx['date'] = order.date_order
        total = self.pool['res.currency'].compute(
            cr, uid, order.currency_id.id, order.company_id.currency_id.id,
            total, context=ctx)
        return self.get_price_from_picking(
            cr, uid, id, total,weight, volume, quantity, context=context)
