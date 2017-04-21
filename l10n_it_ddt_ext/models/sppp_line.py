from openerp import models, exceptions


class StockPickingPackagePreparationLine(models.Model):
    _inherit = 'stock.picking.package.preparation.line'

    def _prepare_lines_from_pickings(self, picking_ids):
        lines = []
        if not picking_ids:
            return lines
        picking_model = self.env['stock.picking']
        for picking in picking_model.browse(picking_ids):
            # picking_has_lines = False
            for move_line in picking.move_lines:
                # ----- If stock move is cancel, don't create package
                #       preparation line
                if move_line.state == 'cancel':
                    continue
                # ----- search if the move is related with a
                #       PackagePreparationLine, yet. If not, create a new line
                if not self.search([('move_id', '=', move_line.id)],
                                   count=True):
                    lines.append({
                        'move_id': move_line.id,
                        'name': move_line.name,
                        'product_id': move_line.product_id.id,
                        'product_uom_qty': move_line.product_uom_qty,
                        'product_uom': move_line.product_uom.id,
                        'lot_id': move_line.restrict_lot_id.id
                        if move_line.restrict_lot_id else False,
                    })
                    # picking_has_lines = True
            # if picking has no move to dogit
            # if not picking_has_lines and \
            #         self.env['stock.picking.package.preparation'].search(
            #             [('picking_ids', '=', picking.id)]):
            #     raise exceptions.ValidationError(
            #         'Picking %s is already full linked to ddt.'
            #         % picking.name
            #     )
        return lines
