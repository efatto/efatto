# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, fields, exceptions, _


class StockPickingPackagePreparation(models.Model):
    _inherit = 'stock.picking.package.preparation'

    @api.model
    def _get_view_type(self):
        action_id = self.env.ref(
            'l10n_it_ddt_mobile.'
            'action_stock_picking_package_preparation_simplified')
        if action_id and self._context.get(
                'params', False):
            if self._context.get(
                    'params').get('action') == action_id.id:
                return True

    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
    )
    product_qty = fields.Float(
        string='Q.ty',
    )
    force_transfer = fields.Boolean(default=_get_view_type)

    @api.multi
    def add_product_in_order(self):
        for pack in self:
            if pack.product_id in pack.line_ids.mapped('product_id'):
                line = pack.line_ids.filtered(lambda r:
                                              r.product_id ==
                                              pack.product_id)
                line.product_uom_qty += pack.product_qty
            else:
                pack.line_ids.create({
                    'product_id': pack.product_id.id,
                    'product_uom_qty': pack.product_qty,
                    'product_uom': pack.product_id.uom_id.id,
                    'name': pack.product_id.name,
                    'package_preparation_id': pack.id,
                    'lot_id': False,
                })

    @api.multi
    def action_put_in_pack(self):
        # update move_ids on line_ids change only if not linked with sale order
        for package in self:
            # update and force assign of picking only if it is a direct ddt
            if package.force_transfer:
                picking_ids = package.line_ids.mapped('move_id.picking_id')
                for picking in picking_ids:
                    flag = True
                    # get only line linked to a picking
                    for line in package.line_ids.filtered(
                            lambda r: r.move_id.picking_id == picking):
                        if line.product_id:
                            #do not change if picking is from sale order
                            if line.move_id.product_uom_qty != \
                                    line.product_uom_qty \
                                    and not picking.group_id:
                                if flag:
                                    picking.action_cancel()
                                    flag = False
                                line.move_id.product_uom_qty = line.\
                                    product_uom_qty
                                line.move_id.product_id = line.product_id
                    picking.force_assign()

                #remove move from picking if it was removed from spp.lines
                for picking in package.picking_ids:
                    flag = True
                    for move in picking.move_lines:
                        if move not in package.line_ids.mapped(
                                'move_id') and not picking.group_id:
                            if flag:
                                picking.action_cancel()
                                flag = False
                            move.unlink()
                    if picking.move_lines:
                        picking.force_assign()
                    #if picking has no more lines, delete it
                    else:
                        picking.unlink()

        return super(StockPickingPackagePreparation, self).action_put_in_pack()
