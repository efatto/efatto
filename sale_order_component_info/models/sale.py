# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    display_qty_component_widget = fields.Boolean(
        compute="_compute_display_qty_component_widget"
    )

    def _compute_display_qty_component_widget(self):
        for line in self:
            line.display_qty_component_widget = (
                line.state in ["draft", "sent"]
                and line.product_id.bom_ids
                and line.qty_to_deliver > 0
            )


class SaleOrder(models.Model):
    _inherit = "sale.order"

    mrp_component_ids = fields.Many2many(
        comodel_name="product.product",
        string="Components",
        compute="_compute_mrp_component_ids",
    )

    def _bom_explode(self, product, products):
        """Add the components of product (and of its sub components) to products.

        In Odoo 18 `mrp.bom._bom_find` takes a `product.product` recordset and
        returns a dict {product: mrp.bom}.
        """
        company_id = self.company_id.id or self.env.company.id
        bom = self.env["mrp.bom"]._bom_find(product, company_id=company_id)[product]
        if bom:
            bom_line_data = bom.explode(product, 1)[1]
            products.extend(
                {
                    "product_id": line.product_id.id,
                    "qty": line_data["qty"],
                    "parent_id": product.id,
                }
                for line, line_data in bom_line_data
            )
            for line_product in [line.product_id for line, _data in bom_line_data]:
                products = self._bom_explode(line_product, products)
        return products

    def _compute_mrp_component_ids(self):
        for order in self:
            order.mrp_component_ids = order.mrp_production_ids.mapped(
                "move_raw_ids.product_id"
            )
