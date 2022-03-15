# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models
from odoo.tools import safe_eval


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _create_delivery_line(self, carrier, price_unit):
        # set price_unit to 0 to manage values on deliveries
        sol = super()._create_delivery_line(carrier, price_unit)
        sol.price_unit = 0.0
        return sol

    def _refresh_delivery_done(self):
        self.ensure_one()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        param = 'delivery_auto_refresh.auto_add_delivery_line'
        if safe_eval(get_param(param, '0')) and self.carrier_id:
            if self.state != 'cancel' or self.invoice_shipping_on_delivery:
                price_unit = self.carrier_id.rate_shipment(self)['price']
                self._create_delivery_line(self.carrier_id, price_unit)
