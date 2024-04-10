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

    def _bom_explode(self, product_id, products):
        bom = self.env["mrp.bom"]._bom_find(
            product=product_id, company_id=self.company_id.id
        )
        if bom:
            bom_line_data = bom.explode(product_id, 1)[1]
            products.extend(
                {
                    "product_id": r[0].product_id.id,
                    "qty": r[1]["qty"],
                    "parent_id": product_id.id,
                }
                for r in bom_line_data
            )
            for product in [r[0].product_id for r in bom_line_data]:
                products = self._bom_explode(product, products)
        return products

    def _compute_mrp_component_ids(self):
        for order in self:
            order.mrp_component_ids = order.production_ids.mapped(
                "move_raw_ids.product_id"
            )
