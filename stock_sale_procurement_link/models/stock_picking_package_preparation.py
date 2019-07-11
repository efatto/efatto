# -*- coding: utf-8 -*-

from openerp import models, fields, api


class StockPickingPackagePreparation(models.Model):
    _inherit = 'stock.picking.package.preparation'

    @api.multi
    def open_procurement_groups(self):
        mod_obj = self.env['ir.model.data']
        act_obj = self.env['ir.actions.act_window']
        action = mod_obj.get_object_reference(
            'stock', 'action_move_form2')
        view = mod_obj.get_object_reference(
            'stock', 'view_move_tree')
        action_id = action and action[1] or False
        action = act_obj.browse(action_id)
        action_vals = action.read()[0]
        action_vals['views'] = [(view and view[1] or False, 'tree')]
        stock_moves = self.env['stock.move'].search([
            ('group_id', 'in', self.mapped('picking_ids.group_id').ids)
        ])
        action_vals['domain'] = [('id', 'in', stock_moves.ids)]
        return action_vals
