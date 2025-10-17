from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    product_expense_account_categ_id = fields.Many2one(
        related="product_id.categ_id.property_account_expense_categ_id",
        store=True,
    )
    product_expense_account_code = fields.Char(
        related="product_expense_account_categ_id.code",
    )
    has_mrp_analytic_lines = fields.Boolean(
        compute="_compute_has_mrp_analytic_lines",
        search="_search_has_mrp_analytic_lines",
    )

    def _get_analytic_info(self):
        self.ensure_one()
        analytic_lines = self.env['account.analytic.line'].browse()
        if (
            self.state != "cancel"
            and self.product_id
            and self.raw_material_production_id
        ):
            analytic_lines = self.env['account.analytic.line'].search([
                ('account_id', '=',
                 self.raw_material_production_id.analytic_account_id.id),
                ('product_id', '=', self.product_id.id),
                ('amount', '<', 0),
            ])
        return analytic_lines

    def _compute_has_mrp_analytic_lines(self):
        for line in self:
            analytic_lines = line._get_analytic_info()
            line.has_mrp_analytic_lines = bool(analytic_lines)

    @api.model
    def _search_has_mrp_analytic_lines(self, operator, value):
        if self.env.context.get("mis_report_filters") or value:
            lines = self.env['stock.move'].browse()
            if self.env.context.get("mis_report_filters"):
                mis_report_filters = self.env.context.get("mis_report_filters")
                if mis_report_filters.get("analytic_account_id"):
                    dict_domain = mis_report_filters.get("analytic_account_id")
                    lines = self.env['stock.move'].search([
                        ("state", "!=", "cancel"),
                        ("product_id", "!=", False),
                        ("raw_material_production_id.analytic_account_id",
                         dict_domain["operator"], dict_domain["value"]),
                    ])
            elif value:
                lines = self.env['stock.move'].search([
                    ("state", "!=", "cancel"),
                    ("product_id", "!=", False),
                    ("raw_material_production_id.analytic_account_id", "=", value),
                ])
            if operator == "!=":
                # this domain is [('has_mrp_analytic_lines', '!=', False)]
                # so we return the lines which has analytic lines with a value or not
                filtered_lines = lines.filtered(
                    lambda l: l._get_analytic_info()
                )
                return [("id", "in", filtered_lines.ids)]
            elif operator == "=":
                # this domain is [('has_mrp_analytic_lines', '=', False)]
                # so we return the lines which hasn't analytic lines with a value or not
                filtered_lines = lines.filtered(
                    lambda l: not l._get_analytic_info()
                )
                return [("id", "in", filtered_lines.ids)]
        return [("id", operator, value)]
