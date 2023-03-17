# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.multi
    @api.depends('product_uom_qty', 'location_dest_id', 'location_id')
    def _set_sign_product_qty(self):
        for move in self:
            move.qty_signed = move.product_uom_qty * (
                -1 if move.location_dest_id.usage in [
                    'customer', 'inventory', 'production', 'procurement',
                    'supplier'
                ] and move.location_id.usage == 'internal' else
                0 if move.location_dest_id.usage in [
                    'customer', 'inventory', 'production', 'procurement',
                    'supplier'
                ] and move.location_id.usage != 'internal' else
                0 if move.location_dest_id.usage == move.location_id.usage
                else 1)

    qty_signed = fields.Float(
        compute=_set_sign_product_qty,
        store=True,
        group_operator="sum"
    )


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.multi
    @api.depends('qty_done', 'location_dest_id', 'location_id')
    def _set_sign_product_qty(self):
        for line in self:
            line.qty_signed = line.qty_done * (
                -1 if line.location_dest_id.usage in [
                    'customer', 'inventory', 'production', 'procurement',
                    'supplier'
                ] and line.location_id.usage == 'internal' else
                0 if line.location_dest_id.usage in [
                    'customer', 'inventory', 'production', 'procurement',
                    'supplier'
                ] and line.location_id.usage != 'internal' else
                0 if line.location_dest_id.usage == line.location_id.usage
                else 1)

    qty_signed = fields.Float(
        compute=_set_sign_product_qty,
        store=True,
        group_operator="sum"
    )
