# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, fields, exceptions, _


class StockPickingPackagePreparation(models.Model):
    _inherit = 'stock.picking.package.preparation'

    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
    )
    product_qty = fields.Float(
        string='Q.ty',
    )

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
        # update move_ids on line_ids change
        for package in self:
            for line in package.line_ids:
                if line.move_id and line.product_id:
                    if line.move_id.picking_id:
                        picking = line.move_id.picking_id
                        if line.move_id.product_uom_qty != \
                                line.product_uom_qty and not picking.group_id:
                            picking.action_cancel()
                            line.move_id.product_uom_qty = line.product_uom_qty
                            line.move_id.product_id = line.product_id
                            picking.force_assign()

            for picking in package.picking_ids:
                for move in picking.move_lines:
                    if move not in package.line_ids.mapped('move_id') and not \
                            picking.group_id:
                        picking.action_cancel()
                        move.unlink()
                        picking.force_assign()

        return super(StockPickingPackagePreparation, self).action_put_in_pack()
