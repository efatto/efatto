# Copyright 2023 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, api
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
    has_mrp_raw_moves = fields.Boolean(
        compute="_compute_has_mrp_raw_moves",
        search="_search_has_mrp_raw_moves",
    )
    mrp_raw_move_ids = fields.Many2many(
        comodel_name="stock.move",
        compute="_compute_mrp_raw_move_ids",
        string="Mrp stock raw moves",
        # not storable as production are not linked here
    )
    mrp_raw_move_unit_amount = fields.Float(
        compute="_compute_mrp_raw_move_ids",
        string="Mrp stock raw moves unit amount",
    )

    def _compute_has_mrp_raw_moves(self):
        for line in self:
            line.has_mrp_raw_moves = bool(line._get_mrp_row_info()[0])

    @api.model
    def _search_has_mrp_raw_moves(self, operator, value):
        if self.env.context.get("mis_report_filters") or value:
            lines = self.env['account.analytic.line'].browse()
            if self.env.context.get("mis_report_filters"):
                mis_report_filters = self.env.context.get("mis_report_filters")
                if mis_report_filters.get("analytic_account_id"):
                    dict_domain = mis_report_filters.get("analytic_account_id")
                    lines = self.env['account.analytic.line'].search([
                        ("product_id", "!=", False),
                        ("account_id", dict_domain["operator"], dict_domain["value"]),
                    ])
            elif value:
                lines = self.env['account.analytic.line'].search([
                    ("product_id", "!=", False),
                    ("account_id", "=", value),
                ])
            if operator == "!=":
                # this domain is [('has_mrp_raw_moves', '!=', False)]
                # so we return the lines which has a mrp_raw_move_ids with a value
                # or not
                filtered_lines = lines.filtered(
                    lambda l: l._get_mrp_row_info()[0]
                )
                return [("id", "in", filtered_lines.ids)]
            elif operator == "=":
                # this domain is [('has_mrp_raw_moves', '=', False)]
                # so we return the lines which hasn't a mrp_raw_move_ids with a value
                # or not
                filtered_lines = lines.filtered(
                    lambda l: not l._get_mrp_row_info()[0]
                )
                return [("id", "in", filtered_lines.ids)]
        return [("id", operator, value)]

    def _get_mrp_row_info(self):
        self.ensure_one()
        mrp_raw_move_unit_amount = self.unit_amount
        mrp_raw_move_ids = self.env['stock.move'].search([
            ("product_id", "=", self.product_id.id),
            ("raw_material_production_id.analytic_account_id",
             "=", self.account_id.id),
            ("state", "!=", "cancel"),
        ])
        # exclude positive lines generated from refunds from computation, but
        # assign them anyway mrp_raw_move_ids to exclude easily from reports
        all_lines = self.env['account.analytic.line'].search([
            ('account_id', '=', self.account_id.id),
            ('product_id', '=', self.product_id.id),
            ('amount', '<', 0),
        ])
        all_lines = all_lines.sorted(
            lambda l: l.invoice_id.date_invoice, reverse=True)
        all_lines = all_lines.sorted(
            lambda l: l.invoice_id.type == 'in_refund')
        qty_consumed_total = sum(mrp_raw_move_ids.mapped("product_uom_qty"))
        if len(all_lines) == 1:
            mrp_raw_move_unit_amount = qty_consumed_total
        else:
            qty_residual = qty_consumed_total
            # compute for all lines onthefly to get the current line amount
            for all_line in all_lines:
                if all_line.unit_amount <= qty_residual:
                    mrp_raw_move_unit_amount = all_line.unit_amount
                    qty_residual -= all_line.unit_amount
                else:
                    mrp_raw_move_unit_amount = qty_residual
                    qty_residual -= qty_residual
                if self == all_lines[-1] and qty_residual:
                    mrp_raw_move_unit_amount += qty_residual
                if all_line == self:
                    break
        return mrp_raw_move_ids, mrp_raw_move_unit_amount

    def _compute_mrp_raw_move_ids(self):
        for line in self:
            if line.product_id:
                mrp_raw_move_ids, mrp_raw_move_unit_amount = line._get_mrp_row_info()
                line.mrp_raw_move_ids = mrp_raw_move_ids
                line.mrp_raw_move_unit_amount = mrp_raw_move_unit_amount
            else:
                line.mrp_raw_move_ids = False
                line.mrp_raw_move_unit_amount = 0.0

    def _compute_extra_cost(self):
        for line in self.sorted(
            lambda l: l.invoice_id.date_invoice, reverse=True
        ):
            if line.invoice_id.type == 'in_invoice':
                # ignore in_refund as qty is computed on consumed qty from production
                # generated analytic lines from refund will be used anyway in method
                # _compute_mrp_raw_move_ids()
                invoice = line.invoice_id
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
                invoice_qty = sum([
                    invoice_line.quantity for invoice_line in
                    product_invoice_lines
                ])
                extra_cost_qty += invoice_qty
                extra_cost_invoice_lines |= product_invoice_lines
                if line.mrp_raw_move_ids:
                    # sum even if the amount is zero, as it could be already fulfilled
                    # in other lines
                    consumed_qty = line.mrp_raw_move_unit_amount
                else:
                    # set all the quantities from the line
                    consumed_qty = extra_cost_qty
                line.extra_cost_unit = float_round(
                    - extra_cost / (extra_cost_qty or 1),
                    precision_digits=2
                )
                line.extra_cost = float_round(
                    - extra_cost / (extra_cost_qty or 1) * consumed_qty,
                    precision_digits=2
                )
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
