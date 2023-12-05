# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    qty_available = fields.Float(related="product_id.qty_available")
    qty_available_at_date_move = fields.Float(
        compute="_compute_qty_available_at_date_move"
    )
    move_line_qty_done = fields.Boolean(compute="_compute_move_line_qty_done")
    sale_partner_id = fields.Many2one(
        string="Sale Partner",
        related="sale_line_id.order_id.partner_id",
    )
    move_origin = fields.Char(
        compute="_compute_move_origin",
        store=False,
    )
    reserve_origin = fields.Selection(
        [
            ("purchase", "Purchase"),
            ("stock", "Stock"),
            ("production", "Production"),
            ("", ""),
        ],
        string="Reserve Origin",
        compute="_compute_reserve",
    )
    reserve_date = fields.Datetime(
        compute="_compute_reserve", string="Max reserve date"
    )
    purchase_ids = fields.Many2many("purchase.order", compute="_compute_reserve")
    production_ids = fields.Many2many("mrp.production", compute="_compute_reserve")

    def _compute_reserve(self):
        for move in self:
            # excludes internal moves
            if (
                move.location_id.usage == "internal"
                and move.location_dest_id.usage == "internal"
            ):
                move.reserve_origin = ""
                move.reserve_date = False
                move.purchase_ids = False
                move.production_ids = False
                continue
            # search RFQ and PO generated for this product
            purchase_order_line_ids = self.env["purchase.order.line"]
            if move.group_id:
                purchase_order_line_ids = self.env["purchase.order.line"].search(
                    [
                        ("procurement_group_id", "=", move.group_id.id),
                        ("product_id", "=", move.product_id.id),
                    ]
                )
            production_ids = move.sale_line_id.order_id.production_ids
            if purchase_order_line_ids:
                purchase_ids = purchase_order_line_ids.mapped("order_id")
                move.reserve_origin = "purchase"
                move.reserve_date = max(purchase_order_line_ids.mapped("date_planned"))
                move.purchase_ids = purchase_ids
                move.production_ids = False
            elif production_ids:
                move.reserve_origin = "production"
                move.reserve_date = max(production_ids.mapped("date_planned_finished"))
                move.purchase_ids = False
                move.production_ids = production_ids
            else:
                move.reserve_origin = "stock"
                move.reserve_date = move.date
                move.purchase_ids = False
                move.production_ids = False

    @api.depends(
        "sale_line_id",
        "production_id",
        "purchase_ids",
        "purchase_line_id",
        "raw_material_production_id",
    )
    def _compute_move_origin(self):
        for move in self:
            move_info = []
            if move.sale_line_id:
                move_info.append(
                    "[OUT] SO: %s %s"
                    % (
                        move.sale_partner_id.name,
                        move.sale_line_id.order_id.name,
                    )
                )
            if move.purchase_line_id:
                move_info.append(
                    "[IN] PO: %s %s"
                    % (
                        move.purchase_line_id.order_id.partner_id.name,
                        move.purchase_line_id.order_id.name,
                    )
                )
            if move.purchase_ids and not move.purchase_line_id:
                move_info.append(
                    "[IN] PO: %s]"
                    % (
                        move.purchase_ids.mapped(
                            lambda x: "%s %s" % (x.partner_id.name, x.name)
                        )
                    )
                )
            if move.production_id:
                move_info.append(
                    "[IN] MO: %s %s %s"
                    % (
                        move.production_id.partner_id.name,
                        move.production_id.sale_id.name,
                        move.production_id.name,
                    )
                )
            if move.raw_material_production_id:
                move_info.append(
                    "[OUT] MO comp.: %s %s %s"
                    % (
                        move.raw_material_production_id.partner_id.name,
                        move.raw_material_production_id.sale_id.name,
                        move.raw_material_production_id.name,
                    )
                )
            if move.inventory_id:
                move_type = "OUT"
                if move.qty_signed > 0:
                    move_type = "IN"
                move_info.append(
                    "[%s] INV: %s %s"
                    % (
                        move_type,
                        move.inventory_id.name,
                        move.inventory_id.date.strftime("%d/%m/%Y"),
                    )
                )
            if (
                not (move.purchase_ids or move.purchase_line_id)
                and move.picking_id
                and move.picking_id.picking_type_id.code == "incoming"
            ):
                move_info.append(
                    "[IN] PICK: %s %s"
                    % (
                        move.picking_id.partner_id.name,
                        move.picking_id.name,
                    )
                )
            move.move_origin = ", ".join(move_info)

    def open_outgoing_move_origin(self):
        self.ensure_one()
        if self.sale_line_id:
            view = self.env.ref("sale.view_order_tree")
            return {
                "type": "ir.actions.act_window",
                "name": _("Reserved Stock: %s") % self.product_id.name,
                "domain": [("id", "=", self.sale_line_id.order_id.id)],
                "views": [(view.id, "tree"), (False, "form")],
                "res_model": "sale.order",
                "context": {},
            }
        if self.raw_material_production_id:
            view = self.env.ref("mrp.mrp_production_tree_view")
            return {
                "type": "ir.actions.act_window",
                "name": _("Reserved Stock: %s") % self.product_id.name,
                "domain": [("id", "=", self.raw_material_production_id.id)],
                "views": [(view.id, "tree"), (False, "form")],
                "res_model": "mrp.production",
                "context": {},
            }
        if self.inventory_id and self.qty_signed < 0:
            view = self.env.ref("stock.view_inventory_tree")
            return {
                "type": "ir.actions.act_window",
                "name": _("Reserved Stock: %s") % self.product_id.name,
                "domain": [("id", "=", self.inventory_id.id)],
                "views": [(view.id, "tree"), (False, "form")],
                "res_model": "stock.inventory",
                "context": {},
            }

    def open_incoming_move_origin(self):
        self.ensure_one()
        if self.purchase_line_id:
            view = self.env.ref("purchase.purchase_order_tree")
            return {
                "type": "ir.actions.act_window",
                "name": _("Reserved Stock: %s") % self.product_id.name,
                "domain": [("id", "=", self.purchase_line_id.order_id.id)],
                "views": [(view.id, "tree"), (False, "form")],
                "res_model": "purchase.order",
                "context": {},
            }
        if self.purchase_ids and not self.purchase_line_id:
            view = self.env.ref("purchase.purchase_order_tree")
            return {
                "type": "ir.actions.act_window",
                "name": _("Reserved Stock: %s") % self.product_id.name,
                "domain": [("id", "in", self.purchase_ids.ids)],
                "views": [(view.id, "tree"), (False, "form")],
                "res_model": "purchase.order",
                "context": {},
            }
        if self.production_id:
            view = self.env.ref("mrp.mrp_production_tree_view")
            return {
                "type": "ir.actions.act_window",
                "name": _("Reserved Stock: %s") % self.product_id.name,
                "domain": [("id", "=", self.production_id.id)],
                "views": [(view.id, "tree"), (False, "form")],
                "res_model": "mrp.production",
                "context": {},
            }
        if self.picking_id and self.picking_id.picking_type_id.code == "incoming":
            view = self.env.ref("stock.view_picking_type_list")
            return {
                "type": "ir.actions.act_window",
                "name": _("Reserved Stock: %s") % self.product_id.name,
                "domain": [("id", "=", self.picking_id.id)],
                "views": [(view.id, "tree"), (False, "form")],
                "res_model": "stock.picking",
                "context": {},
            }
        if self.inventory_id and self.qty_signed > 0:
            view = self.env.ref("stock.view_inventory_tree")
            return {
                "type": "ir.actions.act_window",
                "name": _("Reserved Stock: %s") % self.product_id.name,
                "domain": [("id", "=", self.inventory_id.id)],
                "views": [(view.id, "tree"), (False, "form")],
                "res_model": "stock.inventory",
                "context": {},
            }

    def _compute_move_line_qty_done(self):
        for move in self:
            move.move_line_qty_done = bool(
                any([x.qty_done > 0 for x in move.move_line_ids])
            )

    def _compute_qty_available_at_date_move(self):
        for move in self:
            move.qty_available_at_date_move = move.product_id.with_context(
                {"to_date": move.date}
            ).virtual_available_at_date_move

    def remove_stock_move_reservation(self):
        for move in self:
            wizard = (
                self.env["assign.manual.quants"]
                .with_context(
                    {
                        "active_id": move.id,
                    }
                )
                .create([{}])
            )
            for quants_line in wizard.quants_lines:
                quants_line.qty = 0.0
                quants_line.selected = False
            wizard.assign_quants()
