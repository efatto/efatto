# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    purchase_move_ids = fields.One2many(
        string='Purchase Moves',
        comodel_name='stock.move',
        related='purchase_line_id.move_ids',
    )
    purchase_prod_lot_ids = fields.Many2many(
        comodel_name='stock.production.lot',
        compute='_compute_purchase_prod_lot_ids',
        string="Lots",
    )

    def _compute_purchase_prod_lot_ids(self):
        for line in self:
            line.purchase_prod_lot_ids = line.mapped(
                'purchase_move_ids.move_line_ids.lot_id'
            )
