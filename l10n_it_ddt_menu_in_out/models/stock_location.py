
from odoo import models, fields, api


class StockLocation(models.Model):
    _inherit = 'stock.location'

    type_ddt_id = fields.Many2one(readonly=True, compute='_compute_type_ddt_id')

    @api.multi
    def _compute_type_ddt_id(self):
        for stock_location in self:
            type_ddt_ids = self.env['stock.ddt.type'].search([
                ('stock_location_ids', 'in', stock_location.id)
            ])
            if len(type_ddt_ids) > 1:
                pass
            stock_location.type_ddt_id = type_ddt_ids and type_ddt_ids[0] or False
