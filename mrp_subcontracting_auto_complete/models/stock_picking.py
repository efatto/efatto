from datetime import timedelta

from odoo import models
from odoo.tools.float_utils import float_is_zero


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _action_done(self):
        for picking in self:
            productions_to_done = (
                picking.move_ids._get_recorded_subcontract_production()
            )
            for production in productions_to_done:
                if production.qty_producing < production.product_qty:
                    production.qty_producing = production.product_qty
                    production._set_qty_producing()
                    production.with_context(subcontract_move_id=True).button_mark_done()
                    # For consistency, set the date on production move before the date
                    # on picking. (Traceability report + Product Moves menu item)
                    minimum_date = min(picking.move_line_ids.mapped("date"))
                    production_moves = (
                        production.move_raw_ids | production.move_finished_ids
                    )
                    production_moves.write(
                        {"date": minimum_date - timedelta(seconds=1)}
                    )
                    production_moves.move_line_ids.write(
                        {"date": minimum_date - timedelta(seconds=1)}
                    )
        return super()._action_done()


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _split_productions(
        self, amounts=False, cancel_remaining_qty=False, set_consumed_qty=False
    ):
        # A subcontracted move may carry an extra empty move line. Keeping the
        # zero quantity would create a backorder with ``product_qty = 0`` which
        # violates the ``mrp_production_qty_positive`` constraint. Filter the
        # empty quantities out before splitting.
        if not amounts:
            amounts = {
                production: [
                    production.qty_producing,
                    production._get_quantity_to_backorder(),
                ]
                for production in self
            }
        cleaned_amounts = {}
        for production, quantities in amounts.items():
            rounding = production.product_uom_id.rounding
            quantities = [
                quantity
                for quantity in quantities
                if not float_is_zero(quantity, precision_rounding=rounding)
            ]
            cleaned_amounts[production] = quantities or [production.product_qty]
        return super()._split_productions(
            amounts=cleaned_amounts,
            cancel_remaining_qty=cancel_remaining_qty,
            set_consumed_qty=set_consumed_qty,
        )
