from odoo import models
from datetime import timedelta


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _action_done(self):
        for picking in self:
            productions_to_done = picking._get_subcontracted_productions(
            )._subcontracting_filter_to_done_zero_qty()
            for production in productions_to_done:
                if production.qty_producing == 0:
                    production.qty_producing = production.product_qty
                    production._set_qty_producing()
                    production.with_context(
                        subcontract_move_id=True).button_mark_done()
                    # For consistency, set the date on production move before the date
                    # on picking. (Traceability report + Product Moves menu item)
                    minimum_date = min(picking.move_line_ids.mapped('date'))
                    production_moves = (
                        production.move_raw_ids
                        | production.move_finished_ids)
                    production_moves.write(
                        {'date': minimum_date - timedelta(seconds=1)})
                    production_moves.move_line_ids.write(
                        {'date': minimum_date - timedelta(seconds=1)})
        return super(StockPicking, self)._action_done()


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _subcontracting_filter_to_done_zero_qty(self):
        # REUSE function to filter subcontracting productions, but including productions
        # with zero qty as they are normally not produced automatically (viceversa,
        # partial productions are, wich seems at least akward).

        def filter_in(mo):
            return not (
                mo.state in ("done", "cancel")
                or not all(
                    line.lot_id
                    for line in mo.move_raw_ids.filtered(
                        lambda sm: sm.has_tracking != "none"
                    ).move_line_ids
                )
                or mo.product_tracking != "none"
                and not mo.lot_producing_id
            )

        return self.filtered(filter_in)
