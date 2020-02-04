from datetime import timedelta
from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def update_supplierinfo(self):
        supplierinfo_obj = self.env['product.supplierinfo']
        for line in self.order_line:
            vals = {
                'product_tmpl_id': line.product_id.product_tmpl_id.id,
                'name': line.order_id.partner_id.id,
                'delay': 1,
                'min_qty': 0.0,
                'price': line.price_unit,
                'discount': line.discount,
                'date_start': fields.Date.today(),
                'date_end': False,
                'currency_id': line.order_id.currency_id.id,
            }
            if line.product_id.seller_ids:
                for seller in line.product_id.seller_ids.filtered(
                        lambda x: x.name == line.order_id.partner_id):
                    # Set end valid for all other supplierinfo line for this supplier
                    seller.date_end = fields.Date.today() - timedelta(days=1)
                    vals.update({
                        'delay': seller.delay,
                        'min_qty': seller.min_qty,
                        'product_name': seller.product_name,
                        'product_code': seller.product_code,
                    })
                # Always create a new supplierinfo
                supplierinfo_obj.create(vals)

    @api.multi
    def button_approve(self, force=False):
        res = super().button_approve()
        for order in self:
            order.update_supplierinfo()
        return res
