# Copyright 2023 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _action_done(self):
        res = super()._action_done()
        # only moves linked to a sale or a production have to be updated
        moves_to_do = res.filtered(
            lambda x: x.sale_line_id.order_id.analytic_account_id or
            x.raw_material_production_id.analytic_account_id
        )
        # search account invoice lines and launch updated from them, to include other
        # possible moves to do
        if moves_to_do:
            analytic_accounts = moves_to_do.mapped(
                "sale_line_id.order_id.analytic_account_id"
            ) | moves_to_do.mapped(
                "raw_material_production_id.analytic_account_id")
            invoice_lines = self.env['account.invoice.line'].search([
                ('account_analytic_id', 'in', analytic_accounts.ids),
                ('product_id', 'in', moves_to_do.mapped('product_id.id')),
                ('invoice_type', '=', 'in_invoice'),
            ])
            invoice_lines.account_stock_price_unit_sync()


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    def _action_done(self):
        res = super()._action_done()
        # only moves linked to a sale or a production have to be updated
        move_lines_to_do = self.filtered(
            lambda x: x.move_id.sale_line_id.order_id.analytic_account_id or
            x.move_id.raw_material_production_id.analytic_account_id
        )
        # search account invoice lines and launch updated from them, to include other
        # possible moves to do
        if move_lines_to_do:
            analytic_accounts = move_lines_to_do.mapped(
                "move_id.sale_line_id.order_id.analytic_account_id"
            ) | move_lines_to_do.mapped(
                "move_id.raw_material_production_id.analytic_account_id")
            invoice_lines = self.env['account.invoice.line'].search([
                ('account_analytic_id', 'in', analytic_accounts.ids),
                ('product_id', 'in', move_lines_to_do.mapped('product_id.id')),
                ('invoice_type', '=', 'in_invoice'),
            ])
            if invoice_lines:
                invoice_lines.account_stock_price_unit_sync()

        return res
