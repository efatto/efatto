# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning as UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    sale_partner_invoice_id = fields.Many2one(
        related='sale_id.partner_invoice_id')


class StockDdtType(models.Model):
    _inherit = 'stock.ddt.type'

    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Type of the new Operation', required=False,
        help="This is the picking type associated with the different pickings")


class StockPickingPackagePreparation(models.Model):
    _inherit = 'stock.picking.package.preparation'
    _order = 'ddt_number desc'

    picking_type_ddt_id = fields.Many2one(
        related='ddt_type_id.picking_type_id')

    @api.multi
    def action_put_in_pack(self):
        # Create a stock move and stock picking related with
        # StockPickingPackagePreparationLine if this one has
        # a product in the values
        picking_model = self.env['stock.picking']
        move_model = self.env['stock.move']
        default_picking_type = self.env.user.company_id.\
            default_picking_type_for_package_preparation_id or \
            self.env.ref('stock.picking_type_out')
        pack_model = self.env['stock.pack.operation']
        operation_lot = self.env['stock.pack.operation.lot']
        for package in self:
            # start fix
            # add picking type id from ddt type
            picking_type = package.picking_type_id or \
                           package.picking_type_ddt_id or default_picking_type
            moves = []
            # check partner_invoice_id of order origin of pickings is only 1
            if len(package.picking_ids.mapped('sale_partner_invoice_id.id'))>1:
                raise UserError(
                    _("DDT can contains only pickings with the same partner "
                      "to invoice, as defined in sale order."
                      "Partners: %s. Please remove pickings."
                      % (package.picking_ids.mapped(
                             'sale_partner_invoice_id.name'))))
            # end check
            for line in package.line_ids:
                # If line has 'move_id' this means we don't need to
                # recreate picking and move again
                if (line.product_id and
                        line.product_id.type != 'service' and not
                        line.move_id):
                    move_data = line.get_move_data()
                    move_data.update({
                        'partner_id': package.partner_id.id,
                        'location_id':
                            picking_type.default_location_src_id.id,
                        'location_dest_id':
                            picking_type.default_location_dest_id.id,
                        })
                    moves.append((line, move_data))
            if moves:
                if (
                    not picking_type.default_location_src_id or
                    not picking_type.default_location_dest_id
                ):
                    msg = _(
                        'Cannot find a default location for picking type: %s'
                        % picking_type.name)
                    raise UserError(msg)
                picking_data = {
                    'move_type': 'direct',
                    'partner_id': package.partner_id.id,
                    'company_id': package.company_id.id,
                    'date': package.date,
                    'picking_type_id': picking_type.id,
                    'location_id':
                        picking_type.default_location_src_id.id,
                    'location_dest_id':
                        picking_type.default_location_dest_id.id,
                    }
                picking = picking_model.create(picking_data)
                for line, move_data in moves:
                    move_data.update({'picking_id': picking.id})
                    move = move_model.create(move_data)
                    line.move_id = move.id
                    # Create pack to force lot
                    if line.lot_id:
                        operation = pack_model.create({
                            'product_id': line.product_id.id,
                            'product_uom_id': line.product_uom_id.id,
                            'product_qty': line.product_uom_qty,
                            'qty_done': line.product_uom_qty,
                            'location_id': move_data['location_id'],
                            'location_dest_id': move_data['location_dest_id'],
                            'date': fields.Datetime.now(),
                            'picking_id': picking.id,
                            })
                        operation_lot.create({
                            'operation_id': operation.id,
                            'qty': line.product_uom_qty,
                            'lot_id': line.lot_id.id,
                        })
                # Set the picking as "To DO" and try to set it as
                # assigned
                # skip_update_line_ids because picking is created based on
                # preparation lines, updating lines would erase some fields
                picking = picking.with_context(skip_update_line_ids=True)
                picking.action_confirm()
                # Show an error if a picking is not confirmed
                if picking.state not in ['confirmed', 'assigned']:
                    raise UserError(
                        _('Impossible to create confirmed picking. '
                          'Please Check products availability!'))
                picking.action_assign()
                # Force assign if a picking is not assigned
                if picking.state != 'assigned':
                    picking.force_assign()
                # Show an error if a picking is not assigned
                if picking.state != 'assigned':
                    raise UserError(
                        _('Impossible to create confirmed picking. '
                          'Please Check products availability!'))
                # Add the relation between the new picking
                # and PackagePreparation
                package.picking_ids = [(4, picking.id)]
        return super(StockPickingPackagePreparation, self).action_put_in_pack()
