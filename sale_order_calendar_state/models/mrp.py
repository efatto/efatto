# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    additional_state = fields.Selection(
        [
            ("to_produce", "Waiting material"),
            ("to_assembly", "To assembly"),
            ("to_submanufacture", "To submanufacture"),
            ("to_test", "To test"),
        ],
        string="Additional state",
        copy=False,
    )
    is_blocked = fields.Boolean()
    blocked_note = fields.Char()

    def _post_inventory(self, cancel_backorder=False):
        res = super()._post_inventory(cancel_backorder=cancel_backorder)
        self.write({"additional_state": "to_assembly"})
        return res

    def button_mark_done(self):
        res = super(MrpProduction, self).button_mark_done()
        for mo in self.filtered(lambda x: x.sale_id):
            mo.sale_id.update_forecast_state()
            mo.additional_state = False
        return res

    def button_unmark_additional_state(self):
        self.write({"additional_state": False})

    def button_mark_to_produce(self):
        self.write({"additional_state": "to_produce"})

    def button_mark_to_assembly(self):
        self.write({"additional_state": "to_assembly"})

    def button_mark_to_submanufacture(self):
        self.write({"additional_state": "to_submanufacture"})

    def button_mark_to_test(self):
        self.write({"additional_state": "to_test"})

    def button_mark_not_blocked(self):
        self.write(
            {
                "is_blocked": False,
                "blocked_note": False,
            }
        )
