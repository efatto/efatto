from odoo import fields, models, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    is_analytic_synced = fields.Boolean()
    is_price_synced = fields.Boolean(
        compute="_compute_is_price_synced",
        store=True,
    )
    price_sync_date = fields.Datetime()
    price_date = fields.Datetime()
    has_analytic_account = fields.Boolean(
        compute="_compute_has_analytic_account",
        store=True,
    )

    @api.depends(
        "sale_line_id.order_id.analytic_account_id",
        "raw_material_production_id.analytic_account_id",
    )
    def _compute_has_analytic_account(self):
        for move in self:
            move.has_analytic_account = (
                move.sale_line_id.order_id.analytic_account_id or
                move.raw_material_production_id.analytic_account_id
            )

    @api.depends("is_analytic_synced", "price_sync_date")
    def _compute_is_price_synced(self):
        for move in self:
            move.is_price_synced = (
                move.is_analytic_synced or move.price_sync_date
            )

    def _action_done(self):
        res = super()._action_done()
        # we filter only the moves from internal ubications to not internal, to include
        # sales and productions
        outgoing_moves = res.filtered(
            lambda x: x.location_dest_id.usage != 'internal' and
            x.location_id.usage == 'internal'
        )
        # update separately moves with an analytic account linked to a sale or a
        # production and others
        analytic_moves_to_do = outgoing_moves.filtered(
            lambda x: x.sale_line_id.order_id.analytic_account_id or
            x.raw_material_production_id.analytic_account_id
        )
        other_moves_to_do = outgoing_moves - analytic_moves_to_do
        # search account invoice lines and launch updated from them to include other
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
                ('exclude_extra_cost', '=', False),
            ])
            invoice_lines.account_stock_price_unit_sync()

        if other_moves_to_do:
            # get the last incoming move with account_invoice (or last purchase invoice?)
            invoice_lines = self.env['account.invoice.line'].search([
                ('product_id', 'in', other_moves_to_do.mapped('product_id.id')),
                ('invoice_type', '=', 'in_invoice'),
                ('price_unit', '!=', 0),
                ('quantity', '!=', 0),
                ('exclude_extra_cost', '=', False),
            ])
            invoice_lines.account_stock_price_unit_sync()

        return res
