# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PurchaseOrderTag(models.Model):
    _name = "purchase.order.tag"
    _description = "Purchase order tag"

    name = fields.Char(string="Purchase Order Tag", index=True, required=True)
    active = fields.Boolean(
        default=True,
        help="Set active to false to hide the Purchase Order Tag without removing it.",
    )
    color = fields.Integer()
    order_state = fields.Selection(selection="_get_order_state")
    company_id = fields.Many2one("res.company", string="Company")

    @api.constrains("color", "company_id")
    def _constrains_color_unique(self):
        for rec in self:
            if self.search_count(
                [
                    ("color", "=", rec.color),
                    ("id", "!=", rec.id),
                    ("company_id", "=", rec.company_id.id),
                ]
            ):
                raise UserError(
                    _(
                        "A tag type for the same order state and company already exists"
                        "!"
                    )
                )

    @api.model
    def _get_order_state(self):
        order_state = self.env["purchase.order"]._fields["state"].selection
        return order_state
