from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.depends("product_qty", "product_uom", "company_id", "order_id.partner_id")
    def _compute_price_unit_and_date_planned_and_name(self):
        res = super()._compute_price_unit_and_date_planned_and_name()
        for line in self:
            if not line.product_id or line.invoice_lines or not line.company_id:
                continue
            if line.price_unit == line._origin.price_unit:
                # the price unit has not changed, no need to update it
                continue
            params = line._get_select_sellers_params()
            seller = line.product_id._select_seller(
                partner_id=line.partner_id,
                quantity=line.product_qty,
                date=line.order_id.date_order
                and line.order_id.date_order.date()
                or fields.Date.context_today(line),
                uom_id=line.product_uom,
                params=params,
            )

            # If it was not found an available seller but exist at least a seller,
            # DO NOT use the standard price AS DONE IN ODOO CORE.
            # Use the same logic of v. 12.0
            if not seller:
                if line.product_id.seller_ids.filtered(
                    lambda s, ln=line: s.partner_id.id == ln.partner_id.id
                ):
                    line.price_unit = 0.0
                continue
        return res
