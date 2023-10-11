# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountInvoice(models.Model):
    _inherit = "account.move"

    def write(self, vals):
        res = super().write(vals)
        if "carrier_tracking_ref" in vals:
            sales = self.mapped("invoice_line_ids.sale_line_ids.order_id")
            if sales:
                sales._compute_calendar_state()
        return res
