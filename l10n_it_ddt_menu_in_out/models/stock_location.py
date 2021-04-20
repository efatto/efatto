# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class StockLocation(models.Model):
    _inherit = 'stock.location'

    type_ddt_id = fields.Many2one(readonly=True, compute='_compute_type_ddt_id')

    @api.multi
    def _compute_type_ddt_id(self):
        for stock_location in self:
            type_ddt_id = self.env['stock.ddt.type'].search([
                ('stock_location_ids', 'in', stock_location.id)
            ], order='sequence asc, id asc', limit=1)
            stock_location.type_ddt_id = type_ddt_id or False
