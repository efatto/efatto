# Copyright 2023 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_kit = fields.Boolean(
        string="Is Kit",
        compute="_compute_is_kit",
        search="_search_is_kit",
    )

    @api.depends("product_variant_ids", "product_variant_ids.is_kit")
    def _compute_is_kit(self):
        unique_variants = self.filtered(lambda tmpl: len(tmpl.product_variant_ids) == 1)
        for template in unique_variants:
            template.is_kit = template.product_variant_ids.is_kit
        for template in self - unique_variants:
            template.is_kit = False

    def _search_is_kit(self, operator, value):
        products = self.env["product.product"].search(
            [("is_kit", operator, value)]
        )
        return [("id", "in", products.mapped("product_tmpl_id").ids)]


class ProductProduct(models.Model):
    _inherit = "product.product"

    is_kit = fields.Boolean(string="Is Kit", compute="_compute_is_kit", store=True)

    @api.depends("route_ids", "bom_ids.type")
    def _compute_is_kit(self):
        for product in self:
            product.is_kit = bool(
                any(bom.type == "phantom" for bom in product.bom_ids)
                and self.env.ref("mrp.route_warehouse0_manufacture")
                in product.route_ids
            )
