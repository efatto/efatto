from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    mrp_analytic_line_ids = fields.Many2many(
        comodel_name="account.analytic.line",
        compute="_compute_mrp_analytic_line_ids",
        string="Mrp account analytic lines",
        # not storable
    )

    def _compute_mrp_analytic_line_ids(self):
        for move in self:
            move.mrp_analytic_line_ids = self.env['account.analytic.line'].search([
                ('account_id', '=',
                 move.raw_material_production_id.analytic_account_id.id),
                ('product_id', '=', move.product_id.id),
            ])
