# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models, fields


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    def update_purchase(self):
        super().update_purchase()
        if self.product_id.compute_price_on_weight:
            price_unit = self.price_unit
            # convert price_unit to PO uom_id if different
            if self.uom_id != self.purchase_line_id.product_uom:
                price_unit = self.uom_id._compute_price(
                    price_unit, self.purchase_line_id.product_uom)
            self.purchase_line_id.write({
                'price_unit': price_unit,
            })
            price_unit = self.price_unit
            # convert price_unit to product uom_id if different
            if self.uom_id != self.product_id.uom_id:
                price_unit = self.uom_id._compute_price(
                    price_unit, self.product_id.uom_id)
            supplierinfos = self.env['product.supplierinfo'].search([
                ('name', '=', self.purchase_line_id.order_id.partner_id.id),
                '|',
                ('product_id', '=', self.product_id.id),
                ('product_tmpl_id', '=', self.product_id.product_tmpl_id.id),
            ])
            for supplierinfo in supplierinfos:
                if (
                    supplierinfo.date_end and supplierinfo.date_end >= (
                        self.invoice_id.date_invoice or fields.Date.today()
                    ) or not supplierinfo.date_end
                ) and (
                    supplierinfo.date_start and supplierinfo.date_start <= (
                        self.invoice_id.date_invoice or fields.Date.today()
                    ) or not supplierinfo.date_start
                ):
                    supplierinfo.write({
                        'price': price_unit / self.product_id.weight,
                    })
