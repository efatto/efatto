# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models, fields


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    purchase_force_valid = fields.Boolean()


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    display_update_purchase_button = fields.Boolean(
        compute='_compute_display_update_purchase_button',
        store=True)

    @api.depends("purchase_line_id", "purchase_line_id.price_unit",
                 "purchase_line_id.discount", "purchase_line_id.discount2",
                 "purchase_line_id.discount3", "invoice_id.purchase_force_valid",
                 "price_unit", "discount", "discount2", "discount3")
    def _compute_display_update_purchase_button(self):
        for line in self:
            line.display_update_purchase_button = (
                not line.invoice_id.purchase_force_valid and
                line.purchase_line_id and (
                    line.purchase_line_id.price_unit != line.price_unit or
                    line.purchase_line_id.discount != line.discount or
                    line.purchase_line_id.discount2 != line.discount2 or
                    line.purchase_line_id.discount3 != line.discount3
                )
            )

    def update_purchase(self):
        self.purchase_line_id.write({
            'price_unit': self.uom_id._compute_price(
                self.price_unit, self.purchase_line_id.product_uom
            ),
            'discount': self.discount,
            'discount2': self.discount2,
            'discount3': self.discount3,
        })
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
                    'price': self.uom_id._compute_price(
                        self.price_unit, supplierinfo.product_uom
                    ),
                    'discount': self.discount,
                    'discount2': self.discount2,
                    'discount3': self.discount3,
                })
