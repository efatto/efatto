# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    purchase_move_ids = fields.One2many(
        string='Purchase Moves',
        comodel_name='stock.move',
        related='purchase_line_id.move_ids',
    )
