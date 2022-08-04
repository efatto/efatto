# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        res = super()._prepare_merge_moves_distinct_fields()
        res.append('partner_id')
        return res

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
            if picking:
                if self.origin not in picking.origin:
                    picking.origin = ', '.join([picking.origin or '', self.origin])
        else:
            return super()._search_picking_for_assignation()
        return picking

    def _action_confirm(self, merge=True, merge_into=False):
        if all(self.mapped('rule_id.propagate_partner')):
            for picking in self.mapped('picking_id'):
                picking.onchange_picking_type()
            return super(StockMove, self.with_context(propagate_partner=True)
                         )._action_confirm(merge, merge_into)
        return super()._action_confirm(merge, merge_into)

    def _assign_picking(self):
        """Redefine method to include picking created from multiple origin."""
        if "propagate_partner" not in self.env.context:
            return super()._assign_picking()
        Picking = self.env['stock.picking']
        for move in self:
            recompute = False
            picking = move._search_picking_for_assignation()
            if picking:
                if picking.partner_id.id != move.partner_id.id or (
                    move.origin and move.origin not in (picking.origin or '')
                ):
                    picking.write({
                        'partner_id': False,
                        'origin': False,
                    })
            else:
                recompute = True
                picking = Picking.create(move._get_new_picking_values())
            move.write({'picking_id': picking.id})
            move._assign_picking_post_process(new=recompute)
            if recompute:
                move.recompute()
        return True
