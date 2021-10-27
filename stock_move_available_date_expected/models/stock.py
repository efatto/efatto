# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    qty_available = fields.Float(related='product_id.qty_available')
    qty_available_at_date_expected = fields.Float(
        compute='_compute_qty_available_at_date_expected')
    move_line_qty_done = fields.Boolean(compute='_compute_move_line_qty_done')
    sale_partner_id = fields.Many2one(
        string='Sale Partner',
        related='sale_line_id.order_id.partner_id',
    )

    @api.multi
    def _compute_move_line_qty_done(self):
        for move in self:
            move.move_line_qty_done = bool(any([
                x.qty_done > 0 for x in move.move_line_ids
            ]))

    @api.multi
    def _compute_qty_available_at_date_expected(self):
        for move in self:
            move.qty_available_at_date_expected = move.product_id.with_context(
                {'to_date': move.date_expected}).virtual_available_at_date_expected
