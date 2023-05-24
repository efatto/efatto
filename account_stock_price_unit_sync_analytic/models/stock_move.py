# Copyright 2023 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    is_analytic_synced = fields.Boolean()

    def _action_done(self):
        res = super()._action_done()
        # TODO filtrare solo i movimenti di scarico/consumo
        outgoing_moves = res.filtered(
            lambda x: x.location_dest_id.usage != 'internal' and
            x.location_id.usage == 'internal'
        )
        # TODO eseguire il sync anche sui movimenti senza conto analitico
        # only moves linked to a sale or a production have to be updated
        analytic_moves_to_do = outgoing_moves.filtered(
            lambda x: x.sale_line_id.order_id.analytic_account_id or
            x.raw_material_production_id.analytic_account_id
        )
        other_moves_to_do = outgoing_moves - analytic_moves_to_do
        # search account invoice lines and launch updated from them, to include other
        # possible moves to do
        if analytic_moves_to_do:
            analytic_accounts = analytic_moves_to_do.mapped(
                "sale_line_id.order_id.analytic_account_id"
            ) | analytic_moves_to_do.mapped(
                "raw_material_production_id.analytic_account_id")
            invoice_lines = self.env['account.invoice.line'].search([
                ('account_analytic_id', 'in', analytic_accounts.ids),
                ('product_id', 'in', analytic_moves_to_do.mapped('product_id.id')),
                ('invoice_type', '=', 'in_invoice'),
                ('price_unit', '!=', 0),
                ('quantity', '!=', 0),
            ])
            invoice_lines.account_stock_price_unit_sync()

        if other_moves_to_do:
            # get last incoming move with account_invoice (or last purchase invoice?)
            invoice_lines = self.env['account.invoice.line'].search([
                ('product_id', 'in', other_moves_to_do.mapped('product_id.id')),
                ('invoice_type', '=', 'in_invoice'),
                ('price_unit', '!=', 0),
                ('quantity', '!=', 0),
            ])
            invoice_lines.account_stock_price_unit_sync()

        return res
