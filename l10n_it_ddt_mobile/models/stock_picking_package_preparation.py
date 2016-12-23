# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, exceptions, _


class StockPickingPackagePreparation(models.Model):
    _inherit = 'stock.picking.package.preparation'

    @api.multi
    def action_put_in_pack(self):
        # update move_ids on line_ids change
        for package in self:
            for line in package.line_ids:
                if line.move_id and line.product_id:
                    if line.move_id.picking_id:
                        picking = line.move_id.picking_id
                        if picking.group_id:
                            raise exceptions.Warning(
                                _('Impossible to modify picking \
                                  created from sale order.'))
                        #TODO picking.group_id is not changed
                        if line.move_id.product_uom_qty != line.product_uom_qty:
                            picking.action_cancel()
                            line.move_id.product_uom_qty = line.product_uom_qty
                            line.move_id.product_id = line.product_id
                            picking.force_assign()

            for picking in package.picking_ids:
                if picking.group_id:
                    raise exceptions.Warning(
                        _('Impossible to modify picking \
                          created from sale order.'))
                for move in picking.move_lines:
                    if move not in package.line_ids.mapped('move_id'):
                        picking.action_cancel()
                        move.unlink()
                        picking.force_assign()

        return super(StockPickingPackagePreparation, self).action_put_in_pack()
