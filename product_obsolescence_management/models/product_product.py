from odoo import api, fields, models
from odoo.fields import first


class ProductProduct(models.Model):
    _inherit = "product.product"

    min_stock_qty = fields.Float(
        store=True,
        help="Minimum stock quantity for the product to be stored in the warehouse.",
    )
    is_to_be_replaced = fields.Boolean(
        related="product_state_id.is_end_of_life",
        store=True,
        help="If the product is to be replaced. This flag is related to product state "
        "`end of life` field.",
    )
    replacement_product_ids = fields.Many2many(
        comodel_name="product.product",
        relation="product_product_replacement_rel",
        column1="product_id",
        column2="replacement_product_id",
        help="List of replacement products for the current product. "
        "These products are used when the current product is marked as "
        "`to be replaced`.",
    )
    replacement_product_available_date = fields.Date(
        compute="_compute_replacement_product_available_date",
        store=True,
        help="First date when a purchase order for the replacement product is available"
        ". This date is computed only when a product is `to be replaced` and has "
        "at least one purchase order line in state `purchase` or `done`.",
    )

    @api.depends("is_to_be_replaced", "replacement_product_ids.purchase_order_line_ids")
    def _compute_replacement_product_available_date(self):
        for r in self:
            purchase_lines = r.replacement_product_ids.purchase_order_line_ids.filtered(
                lambda pol: pol.state in ["purchase", "done"]
            )
            if r.is_to_be_replaced and purchase_lines:
                r.replacement_product_available_date = first(
                    purchase_lines
                ).date_planned
            else:
                r.replacement_product_available_date = False

    def update_product_state(self):
        orderpoint_obj = self.env["stock.warehouse.orderpoint"]
        for product in self:
            product.min_stock_qty = int(
                sum(
                    self.env["sale.order.line"]
                    .search(
                        [
                            ("product_id", "=", product.id),
                            ("state", "in", ["sale", "done"]),
                        ]
                    )
                    .mapped("product_uom_qty")
                )
                / 10
            )
            if (
                not product.replacement_product_available_date
                and product.replacement_product_ids
            ):
                # TODO create an op for the first replacement product using the op of
                #  the to be replaced product
                orderpoints = orderpoint_obj.search([("product_id", "=", product.id)])
                if not orderpoints:
                    # search the first deactivated op if not found
                    orderpoints = orderpoint_obj.with_context(active_test=False).search(
                        [("product_id", "=", product.id)]
                    )
                if orderpoints:
                    first(product.replacement_product_ids)
                    # todo create op for the replacement product (using an existing method?)
