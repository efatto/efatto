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
        help="Lead time in days to purchase this product. "
        "Computed from delay of first seller.",
    )
    purchase_multiple_qty = fields.Float(
        "Purchase Multiple Qty",
        compute="_compute_purchase_delay",
        inverse="_inverse_purchase_delay",
        store=True,
        help="Purchase multiple quantity to purchase this product. "
        "Computed from multiple quantity of first seller.",
    )

    def _get_first_seller(self):
        sellers = self.seller_ids.filtered(
            lambda s: not s.date_end or s.date_end >= fields.Date.context_today(self)
        )
        if sellers:
            return sellers.sorted(key=lambda s: (s.sequence, -s.min_qty, s.price, s.id))[0]
        return self.env["product.supplierinfo"]

    @api.depends("seller_ids", "seller_ids.delay", "seller_ids.multiple_qty",
                 "seller_ids.date_end", "seller_ids.sequence", "purchase_ok")
    def _compute_purchase_delay(self):
        for product_tmpl in self:
            purchase_delay = 0.0
            purchase_multiple_qty = 1.0
            if product_tmpl.purchase_ok:
                seller_id = self._get_first_seller()
                if seller_id:
                    if seller_id.delay:
                        purchase_delay = seller_id.delay
                    if seller_id.multiple_qty:
                        purchase_multiple_qty = seller_id.multiple_qty
            product_tmpl.purchase_delay = purchase_delay
            product_tmpl.purchase_multiple_qty = purchase_multiple_qty

    def _inverse_purchase_delay(self):
        for product_tmpl in self:
            if product_tmpl.purchase_ok:
                seller_id = self._get_first_seller()
                if seller_id:
                    if product_tmpl.purchase_delay:
                        seller_id.delay = product_tmpl.purchase_delay
                    if product_tmpl.purchase_multiple_qty:
                        seller_id.multiple_qty = product_tmpl.purchase_multiple_qty
