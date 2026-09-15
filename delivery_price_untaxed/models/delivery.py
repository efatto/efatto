from odoo import fields, models


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    use_price_untaxed = fields.Boolean()

    def _get_price_available(self, order):
        res = super()._get_price_available(order=order)
        if not self.use_price_untaxed:
            return res
        self = self.sudo()
        order = order.sudo()
        total = weight = volume = quantity = wv = 0
        for line in order.order_line:
            if line.state == "cancel":
                continue
            if line.product_id.type in {"service", "combo"}:
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
            wv += (
                (line.product_id.weight or 0.0) * (line.product_id.volume or 0.0) * qty
            )
            quantity += qty

        total = self._compute_currency(order, total, "pricelist_to_company")
        # weight is either,
        # 1- weight chosen by user in choose.delivery.carrier wizard passed by context
        # 2- saved weight to use on sale order
        # 3- total order line weight as fallback
        weight = self.env.context.get("order_weight") or order.shipping_weight or weight

        return self._get_price_from_picking(total, weight, volume, quantity, wv=wv)
