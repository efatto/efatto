# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockDeliveryNoteLine(models.Model):
    _inherit = "stock.delivery.note.line"

    client_order_ref = fields.Char(
        related="sale_line_id.order_id.client_order_ref",
        string="Sale Customer Reference",
    )
