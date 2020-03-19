from datetime import timedelta
from odoo import models, fields, api


class SupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    purchase_order_id = fields.Many2one(
        comodel_name='purchase.order',
        string='Purchase Order',
        help='Purchase order generator of this line, if exists.'
    )


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def update_supplierinfo(self):
        supplierinfo_obj = self.env['product.supplierinfo']
        for line in self.order_line.filtered(
            lambda x: x.price_unit != 0.0 and x.product_id.seller_ids
        ):
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
                'purchase_order_id': line.order_id.id,
            }
            update = False
            for seller in line.product_id.seller_ids.filtered(
                    lambda x: x.name == line.order_id.partner_id):
                if seller.price != line.price_unit \
                        or seller.discount != line.discount:
                    # Set invalid all other supplierinfo line for this supplier
                    seller.date_end = fields.Date.today() - timedelta(days=1)
                    vals.update({
                        'delay': seller.delay,
                        'min_qty': seller.min_qty,
                        'product_name': seller.product_name,
                        'product_code': seller.product_code,
                    })
                if seller.purchase_order_id == self:
                    seller.write(vals)
                    update = True
            if not update:
                supplierinfo_obj.create(vals)

    @api.multi
    def button_approve(self, force=False):
        res = super().button_approve()
        for order in self:
            order.update_supplierinfo()
        return res
