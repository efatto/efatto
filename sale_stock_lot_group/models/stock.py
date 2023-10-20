# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProductionLot(models.Model):
    _inherit = "stock.production.lot"

    @api.depends("name")
    def _compute_sale_order_ids(self):
        for lot in self:
            stock_moves = (
                self.env["stock.move.line"]
                .search([("lot_id", "=", lot.id), ("state", "=", "done")])
                .mapped("move_id")
            )
            stock_moves = stock_moves.search([("id", "in", stock_moves.ids)]).filtered(
                lambda move: move.picking_id.location_dest_id.usage == "customer"
                and move.state == "done"
            )
            lot.sale_order_ids = stock_moves.sudo().mapped("sale_line_id.order_id")
            lot.sale_order_count = len(lot.sale_order_ids)
