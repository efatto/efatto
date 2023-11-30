# Copyright 2023 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.onchange('product_qty', 'product_uom', 'company_id')
    def _onchange_quantity(self):
        if not self.product_id or self.invoice_lines or not self.company_id:
            return
        params = {'order_id': self.order_id}
        seller = self.product_id._select_seller(
            partner_id=self.partner_id,
            quantity=self.product_qty,
            date=self.order_id.date_order and self.order_id.date_order.date(),
            uom_id=self.product_uom,
            params=params)

        if seller or not self.date_planned:
            self.date_planned = self._get_date_planned(seller).strftime(
                DEFAULT_SERVER_DATETIME_FORMAT)

        # If not seller, DO NOT use the standard price AS DONE IN ODOO CORE.
        # Use the same logic of v. 12.0
        if not seller:
            if self.product_id.seller_ids.filtered(
                    lambda s: s.name.id == self.partner_id.id):
                self.price_unit = 0.0
            return
        super()._onchange_quantity()
