# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    qty_available_at_date_expected = fields.Float(
        compute='_compute_qty_available_at_date_expected')

    @api.multi
    def _compute_qty_available_at_date_expected(self):
        for move in self:
            move.qty_available_at_date_expected = move.product_id.with_context(
                {'to_date': move.date_expected}).virtual_available_at_date_expected
