# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    draft_purchase_order_qty = fields.Float(
        string="Purchase RdP On Location",
        compute="_compute_product_purchase_qty",
        digits="Product Unit of Measure",
    )
    virtual_location_missing_qty = fields.Float(
        string="Virtual missing Qty On Location",
        help="Only negative values are meaningful",
        compute="_compute_product_purchase_qty",
        digits="Product Unit of Measure",
    )
    is_virtual_location_missing_qty = fields.Boolean(
        string="Is Virtual missing Qty On Location",
        compute="_compute_product_purchase_qty",
        search="_search_is_virtual_location_missing_qty",
    )

    def _search_is_virtual_location_missing_qty(self, operator, value):
        ops = self.search([("product_min_qty", ">", 0)], limit=None)
        ops = ops.filtered(lambda x: x.qty_forecast < x.product_min_qty)
        return [("id", "in", ops.ids)]

    @api.depends("product_id", "location_id", "qty_forecast", "product_min_qty")
    def _compute_product_purchase_qty(self):
        for op in self:
            # Core `qty_forecast` already includes the draft/sent purchase orders
            # (see `purchase_stock._quantity_in_progress`). Expose that RFQ
            # quantity separately, reusing the very same core helper.
            qty_by_product_location, _dummy = op.product_id._get_quantity_in_progress(
                location_ids=op.location_id.ids
            )
            purchase_qty = qty_by_product_location.get(
                (op.product_id.id, op.location_id.id), 0.0
            )
            if op.product_id and op.product_uom:
                purchase_qty = op.product_id.uom_id._compute_quantity(
                    purchase_qty, op.product_uom, round=False
                )
            # `qty_forecast` is the availability including draft/sent POs, so the
            # missing quantity is simply its gap with the minimum.
            virtual_missing_qty = min(op.qty_forecast - op.product_min_qty, 0)
            if op.product_id.is_kits:
                virtual_missing_qty = 0
            op.update(
                {
                    "draft_purchase_order_qty": purchase_qty,
                    "virtual_location_missing_qty": virtual_missing_qty,
                    "is_virtual_location_missing_qty": virtual_missing_qty < 0,
                }
            )
