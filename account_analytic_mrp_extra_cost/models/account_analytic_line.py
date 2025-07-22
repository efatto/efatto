# Copyright 2023 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.tools.float_utils import float_round


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    extra_cost = fields.Float(
        string="Actual Cost Total",
        compute="_compute_extra_cost",
    )
    extra_cost_unit = fields.Float(
        string="Actual Cost Unit",
        compute="_compute_extra_cost",
    )
    extra_cost_qty = fields.Float(
        string="Actual Cost Quantity",
        compute="_compute_extra_cost",
    )
    # row without a product must be added to mis builder directly for the entire amount
    extra_cost_invoice_line_ids = fields.Many2many(
        string="Actual Cost Invoice Lines",
        comodel_name="account.invoice.line",
        compute="_compute_extra_cost",
    )
    invoice_id = fields.Many2one(related='move_id.invoice_id')
    mrp_raw_move_ids = fields.Many2many(
        comodel_name="stock.move",
        compute="_compute_mrp_raw_move_ids",
        string="Mrp stock raw moves",
        # not storable as production are not linked here
    )

    def _compute_mrp_raw_move_ids(self):
        for line in self:
            mrp_raw_move_ids = self.env['stock.move'].browse()
            if line.product_id or line.move_id.product_id:
                mrp_raw_move_ids = self.env['stock.move'].search([
                    ("product_id", "=", (line.product_id | line.move_id.product_id).id),
                    ("raw_material_production_id.analytic_account_id",
                     "=", line.account_id.id),
                    ("state", "!=", "cancel"),
                ])
            line.mrp_raw_move_ids = mrp_raw_move_ids

    def _compute_extra_cost(self):
        for line in self:
            if line.move_id.invoice_id.type in [
                'in_invoice', 'in_refund'
            ]:
                invoice = line.move_id.invoice_id
                product_invoice_lines = invoice.invoice_line_ids.filtered(
                    lambda x: x.account_analytic_id == line.account_id
                    and x.account_id == line.general_account_id
                    and x.product_id == line.product_id
                    and not x.exclude_extra_cost
                )
                extra_cost = 0.0
                extra_cost_qty = 0.0
                extra_cost_invoice_lines = self.env["account.invoice.line"]
                # invoice_cost and raw_move_cost and extra_cost are positive when
                # they are costs, viceversa they are income if they are negative
                invoice_cost = sum([
                    invoice_line.price_subtotal_signed for invoice_line in
                    product_invoice_lines
                ])
                extra_cost += float_round(
                    invoice_cost,
                    precision_rounding=invoice.currency_id.rounding,
                )
                invoice_qty = sum([  # todo check if refund is negative!
                    invoice_line.quantity for invoice_line in
                    product_invoice_lines
                ])
                extra_cost_qty += invoice_qty
                extra_cost_invoice_lines |= product_invoice_lines
                if line.mrp_raw_move_ids:
                    consumed_qty = sum(line.mapped('mrp_raw_move_ids.product_uom_qty'))
                else:
                    # impute all the quantity from the line
                    consumed_qty = extra_cost_qty
                line.extra_cost_unit = - extra_cost / extra_cost_qty
                line.extra_cost = - extra_cost / extra_cost_qty * consumed_qty
                line.extra_cost_qty = consumed_qty
                if extra_cost_invoice_lines:
                    line.extra_cost_invoice_line_ids = [
                        (6, 0, extra_cost_invoice_lines.ids)]
                else:
                    line.extra_cost_invoice_line_ids = False
            else:
                line.extra_cost = 0.0
                line.extra_cost_unit = 0.0
                line.extra_cost_qty = 0.0
                line.extra_cost_invoice_line_ids = False
