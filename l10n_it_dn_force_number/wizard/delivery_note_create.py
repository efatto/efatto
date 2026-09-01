# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockDeliveryNoteCreateWizard(models.TransientModel):
    _inherit = "stock.delivery.note.create.wizard"

    name = fields.Char()

    def confirm(self):
        res = super().confirm()
        if self.name and res.get("res_id"):
            delivery_note = self.env["stock.delivery.note"].browse(res["res_id"])
            delivery_note.write({"name": self.name})
        return res

    def _prepare_delivery_note_vals(self, sale_order_id):
        res = super()._prepare_delivery_note_vals(sale_order_id=sale_order_id)
        carrier_tracking_ref = ", ".join(
            {
                pick.carrier_tracking_ref
                for pick in self.selected_picking_ids.filtered(
                    lambda x: x.carrier_tracking_ref
                )
            }
        )
        if carrier_tracking_ref:
            res["carrier_tracking_ref"] = carrier_tracking_ref
        return res
