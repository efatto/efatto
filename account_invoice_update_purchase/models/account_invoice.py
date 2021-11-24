# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    display_update_purchase_button = fields.Boolean(
        compute='_compute_display_update_purchase_button')

    def _compute_display_update_purchase_button(self):
        for line in self:
            line.display_update_purchase_button = (
                line.purchase_line_id and (
                    line.purchase_line_id.price_unit != line.price_unit or
                    line.purchase_line_id.discount != line.discount or
                    line.purchase_line_id.discount2 != line.discount2 or
                    line.purchase_line_id.discount3 != line.discount3
                )
            )

    def update_purchase(self):
        # OK stock move is updated
        # OK cost of the product is updated
        # TODO
        #  supplierinfo: how to? and really to do?
        #  others ?
        self.purchase_line_id.write({
           'price_unit': self.price_unit,
           'discount': self.discount,
           'discount2': self.discount2,
           'discount3': self.discount3,
        })
