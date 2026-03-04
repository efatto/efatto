# Copyright 2023 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class SupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    multiple_qty = fields.Float(default=1.0)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    purchase_delay = fields.Float(
        string="Purchase Lead Time (computed)",
        compute="_compute_purchase_delay",
        inverse="_inverse_purchase_delay",
        store=True,
        default=0.0,
        help="Lead time in days to purchase this product. "
        "Computed from delay of first seller.",
    )
    purchase_multiple_qty = fields.Float(
        "Purchase Multiple Qty",
        compute="_compute_purchase_delay",
        inverse="_inverse_purchase_delay",
        store=True,
        default=1.0,
        help="Purchase multiple quantity to purchase this product. "
        "Computed from multiple quantity of first seller.",
    )

    @api.depends("seller_ids", "seller_ids.delay", "purchase_ok")
    def _compute_purchase_delay(self):
        for product_tmpl in self:
            if (
                product_tmpl.seller_ids.filtered(
                    lambda s: not s.date_end or s.date_end >= fields.Date.today()
                )
                and product_tmpl.purchase_ok
            ):
                seller_id = fields.first(
                    product_tmpl.seller_ids.filtered(
                        lambda s: not s.date_end or s.date_end >= fields.Date.today()
                    )
                )
                product_tmpl.purchase_delay = seller_id.delay
                product_tmpl.purchase_multiple_qty = seller_id.multiple_qty
            else:
                product_tmpl.purchase_delay = 0

    def _inverse_purchase_delay(self):
        for product_tmpl in self:
            if product_tmpl.seller_ids.filtered(
                lambda s: not s.date_end or s.date_end >= fields.Date.today()
            ):
                seller_id = fields.first(
                    product_tmpl.seller_ids.filtered(
                        lambda s: not s.date_end or s.date_end >= fields.Date.today()
                    )
                )
                seller_id.delay = product_tmpl.purchase_delay
                seller_id.multiple_qty = product_tmpl.purchase_multiple_qty
