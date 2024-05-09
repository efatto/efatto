# Copyright 2017-2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProviderGrid(models.Model):
    _inherit = "delivery.carrier"

    def _get_price_available(self, order):
        super()._get_price_available(order)
        self.ensure_one()
        total = weight = volume = quantity = 0
        for line in order.order_line:
            if line.state == "cancel":
                continue
            if not line.is_delivery:
                total += line.price_subtotal
            if not line.product_id or line.is_delivery:
                continue
            qty = line.product_uom._compute_quantity(
                line.product_uom_qty, line.product_id.uom_id
            )
            weight += (line.product_id.weight or 0.0) * qty
            volume += (line.product_id.volume or 0.0) * qty
            quantity += qty

        total = order.currency_id._convert(
            total,
            order.company_id.currency_id,
            order.company_id,
            order.date_order or fields.Date.today(),
        )
        return self._get_price_from_picking(total, weight, volume, quantity)
