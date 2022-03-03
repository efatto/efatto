# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        return [
            'product_id', 'price_unit', 'product_packaging', 'procure_method',
            'product_uom', 'restrict_partner_id', 'scrapped', 'origin_returned_move_id',
            'package_level_id', 'partner_id'
        ]

    def _search_picking_for_assignation(self):
        self.ensure_one()
        if self.partner_id:
            picking = self.env['stock.picking'].search([
                ('partner_id', '=', self.partner_id.id),
                ('group_id', '=', self.group_id.id),
                ('location_id', '=', self.location_id.id),
                ('location_dest_id', '=', self.location_dest_id.id),
                ('picking_type_id', '=', self.picking_type_id.id),
                ('printed', '=', False),
                ('state', 'in', ['draft', 'confirmed', 'waiting', 'assigned'])
            ], limit=1)
        else:
            return super()._search_picking_for_assignation()
        return picking
