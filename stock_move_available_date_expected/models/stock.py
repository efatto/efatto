# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    qty_available = fields.Float(related='product_id.qty_available')
    qty_available_at_date_expected = fields.Float(
        compute='_compute_qty_available_at_date_expected')
    move_line_qty_done = fields.Boolean(compute='_compute_move_line_qty_done')
    sale_partner_id = fields.Many2one(
        string='Sale Partner',
        related='sale_line_id.order_id.partner_id',
    )
    move_origin = fields.Char(
        compute='_compute_move_origin',
        store=True,
    )
    reserve_origin = fields.Selection([
        ('purchase', 'Purchase'),
        ('stock', 'Stock'),
        ('production', 'Production'),
        ('', ''),
    ], string="Reserve Origin",
        compute='_compute_reserve')
    reserve_date = fields.Datetime(
        compute='_compute_reserve',
        string="Max reserve date")
    purchase_ids = fields.Many2many(
        'purchase.order',
        compute='_compute_reserve')
    production_ids = fields.Many2many(
        'mrp.production',
        compute='_compute_reserve')

    @api.multi
    def _compute_reserve(self):
        for move in self:
            # excludes internal and in moves
            if (move.location_id.usage == 'internal' and
                move.location_dest_id.usage == 'internal') or (
                move.location_id.usage != 'internal' and
                move.location_dest_id.usage == 'internal'
            ):
                move.reserve_origin = ''
                move.reserve_date = False
                move.purchase_ids = False
                continue
            # search RFQ and PO generated for this product
            purchase_order_line_ids = self.env['purchase.order.line'].search([
                ('procurement_group_id', '=', move.group_id.id),
                ('product_id', '=', move.product_id.id),
            ])
            if not purchase_order_line_ids:
                move_origin_ids = self.env['stock.move'].search([
                    ('move_dest_ids', 'in', move.ids)
                ])
                if move_origin_ids:
                    purchase_order_line_ids = move_origin_ids.mapped('purchase_line_id')
            production_ids = move.sale_line_id.order_id.production_ids
            if purchase_order_line_ids:
                purchase_ids = purchase_order_line_ids.mapped('order_id')
                move.reserve_origin = 'purchase'
                move.reserve_date = max(purchase_order_line_ids.mapped('date_planned'))
                move.purchase_ids = purchase_ids
            elif production_ids:
                move.reserve_origin = 'production'
                move.reserve_date = max(production_ids.mapped('date_planned_finished'))
                move.production_ids = production_ids
            else:
                move.reserve_origin = 'stock'
                move.reserve_date = move.date_expected
                move.purchase_ids = False

    @api.multi
    @api.depends('sale_line_id', 'purchase_line_id', 'production_id',
                 'raw_material_production_id')
    def _compute_move_origin(self):
        for move in self:
            move_info = []
            if move.sale_line_id:
                move_info.append(
                    '[SO: %s %s]' % (
                        move.sale_partner_id.name,
                        move.sale_line_id.order_id.name,
                    ))
            if move.purchase_line_id:
                move_info.append(
                    '[PO: %s %s]' % (
                        move.purchase_line_id.order_id.partner_id.name,
                        move.purchase_line_id.order_id.name,
                    ))
            if move.production_id:
                move_info.append(
                    '[MO: %s %s %s]' % (
                        move.production_id.partner_id.name,
                        move.production_id.sale_id.name,
                        move.production_id.name,
                    ))
            if move.raw_material_production_id:
                move_info.append(
                    '[MO consumed: %s %s %s]' % (
                        move.raw_material_production_id.partner_id.name,
                        move.raw_material_production_id.sale_id.name,
                        move.raw_material_production_id.name,
                    ))
            move.move_origin = ', '.join(move_info)

    @api.multi
    def _compute_move_line_qty_done(self):
        for move in self:
            move.move_line_qty_done = bool(any([
                x.qty_done > 0 for x in move.move_line_ids
            ]))

    @api.multi
    def _compute_qty_available_at_date_expected(self):
        for move in self:
            move.qty_available_at_date_expected = move.product_id.with_context(
                {'to_date': move.date_expected}).virtual_available_at_date_expected

    @api.multi
    def remove_stock_move_reservation(self):
        for move in self:
            wizard = self.env['assign.manual.quants'].with_context({
                'active_id': move.id,
            }).create({})
            for quants_line in wizard.quants_lines:
                quants_line.qty = 0.0
                quants_line.selected = False
            wizard.assign_quants()
