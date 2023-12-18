# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    include_draft_purchase = fields.Boolean()
    draft_purchase_order_qty = fields.Float(
        string="Purchase RdP On Location", compute="_compute_product_purchase_qty"
    )
    virtual_location_draft_purchase_qty = fields.Float(
        string="Virtual with RdP On Location", compute="_compute_product_purchase_qty"
    )
    virtual_location_missing_qty = fields.Float(
        string="Virtual missing Qty On Location",
        compute="_compute_product_purchase_qty",
    )
    is_virtual_location_missing_qty = fields.Boolean(
        string="Is Virtual missing Qty On Location",
        compute="_compute_product_purchase_qty",
        search="_search_is_virtual_location_missing_qty",
    )

    def _search_is_virtual_location_missing_qty(self, operator, value):
        ops = self.env["stock.warehouse.orderpoint"].search(
            [("product_min_qty", ">", 0)], limit=None
        )
        ops = ops.filtered(
            lambda x: x.product_min_qty > x.virtual_location_draft_purchase_qty
        )
        return [("id", "in", ops.ids)]

    def _compute_product_purchase_qty(self):
        for op in self:
            purchase_order_line_ids = self.env["purchase.order.line"].search(
                [
                    ("state", "in", ["draft", "sent"]),
                    ("product_id", "=", op.product_id.id),
                    ("orderpoint_id.location_id", "=", op.location_id.id),
                    ("orderpoint_id", "=", op.id),
                ]
            )
            purchase_qty = sum(purchase_order_line_ids.mapped("product_uom_qty") or [0])
            virtual_draft_purchase_qty = op.virtual_location_qty + purchase_qty
            virtual_missing_qty = virtual_draft_purchase_qty - op.product_min_qty
            op.update(
                {
                    "draft_purchase_order_qty": purchase_qty,
                    "virtual_location_draft_purchase_qty": virtual_draft_purchase_qty,
                    "virtual_location_missing_qty": virtual_missing_qty,
                    "is_virtual_location_missing_qty": True
                    if virtual_missing_qty < 0
                    else False,
                }
            )


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    @api.model
    def run(self, procurements, raise_user_error=True):
        for procurement in procurements:
            # subtract qty in PO in draft and sent states for current OP
            if procurement.values.get("orderpoint_id"):
                orderpoint_id = procurement.values["orderpoint_id"]
                if (
                    orderpoint_id.include_draft_purchase
                    and (
                        orderpoint_id.draft_purchase_order_qty
                        + orderpoint_id.incoming_location_qty
                        + orderpoint_id.product_location_qty
                        - orderpoint_id.outgoing_location_qty
                    )
                    >= orderpoint_id.product_min_qty
                ):
                    return False
        return super().run(procurements, raise_user_error=raise_user_error)
