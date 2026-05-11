from odoo import _, models
from odoo.exceptions import UserError


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    def _check_create(self):
        super()._check_create()
        if self.env.user.has_group(
            "stock.group_stock_user"
        ) and not self.env.user.has_group(
            "stock_production_lot_group_create.group_production_lot_manager"
        ):
            active_picking_id = self.env.context.get("active_picking_id", False)
            if not active_picking_id:
                raise UserError(
                    _(
                        "You are not allowed to create a lot or serial number manually."
                        "\nPlease create it from a stock picking with an appropriate "
                        "operation type."
                    )
                )
            picking_id = self.env["stock.picking"].browse(active_picking_id)
            if picking_id and not picking_id.picking_type_id.use_create_lots:
                raise UserError(
                    _(
                        "You are not allowed to create a lot or serial number with this"
                        " operation type. To change this, go on the operation type and "
                        "tick the box 'Create New Lots/Serial Numbers'."
                    )
                )
