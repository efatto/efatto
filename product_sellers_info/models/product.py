from odoo import api, fields, models


class SupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    multiple_qty = fields.Float(default=1.0)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    purchase_delay = fields.Float(
        'Purchase Lead Time', compute='_get_purchase_delay',
        store=True, default=0.0,
        help="Lead time in days to purchase this product. "
             "Computed from delay of first seller.")
    purchase_multiple_qty = fields.Float(
        'Purchase Multiple Qty', compute='_get_purchase_delay',
        store=True, default=1.0,
        help="Purchase multiple quantity to purchase this product. "
             "Computed from multiple quantity of first seller.")

    @api.depends('seller_ids', 'seller_ids.delay')
    def _get_purchase_delay(self):
        for product_tmpl in self:
            if product_tmpl.seller_ids and product_tmpl.purchase_ok:
                product_tmpl.purchase_delay = product_tmpl.seller_ids[0].delay
                product_tmpl.purchase_multiple_qty = \
                    product_tmpl.seller_ids[0].multiple_qty
            else:
                product_tmpl.purchase_delay = 0
