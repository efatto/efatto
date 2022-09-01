# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    enable_reserve_date_check = fields.Boolean(
        help="Forbid reservation on not possible date",
        default=True, copy=False)

    @api.multi
    def action_confirm(self):
        # Add variable in context to enable check
        for order in self:
            super(SaleOrder, self.with_context(
                enable_reserve_date_check=order.enable_reserve_date_check
            )).action_confirm()
        return True
