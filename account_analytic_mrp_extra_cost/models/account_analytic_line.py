# Copyright 2023 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, _
from odoo.exceptions import ValidationError


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    extra_cost = fields.Float(
        compute="_compute_extra_cost",
    )
    extra_cost_invoice_line_ids = fields.Many2many(
        comodel_name="account.invoice.line",
        compute="_compute_extra_cost",
    )

    def _compute_extra_cost(self):
        for line in self:
            if line.move_id.invoice_id.type in [
                'in_invoice', 'in_refund'
            ]:
                """
                N.B. this function work only if it creates analytic lines grouped by
                account, with account_group_invoice_line and journal has active option
                'group_invoice_lines': True,
                'group_method': 'account',
                So add an error if not configured in this way.
                """
                invoice = line.move_id.invoice_id
                if not (invoice.journal_id.group_invoice_lines and
                        invoice.journal_id.group_method == 'account'):
                    raise ValidationError(_(
                        "Invoice journal %s is not configured with grouped lines "
                        "option by account!" % invoice.journal_id.name
                    ))
                all_invoice_lines = invoice.invoice_line_ids.filtered(
                    lambda x: x.account_analytic_id == line.account_id
                    and x.account_id == line.general_account_id
                )
                no_product_invoice_lines = all_invoice_lines.filtered(
                    lambda y: not y.product_id
                )
                invoice_lines = all_invoice_lines - no_product_invoice_lines
                products = invoice_lines.mapped('product_id')
                raw_mo_moves = self.env['stock.move'].search([
                    ('raw_material_production_id.analytic_account_id', '=',
                     line.account_id.id),
                ])
                raw_products = raw_mo_moves.mapped('product_id')
                # create dicts with {product: lines}
                raw_move_by_product = {product: raw_mo_moves.filtered(
                    lambda y: y.product_id == product
                ) for product in raw_products}
                invoice_line_by_products = {product: invoice_lines.filtered(
                    lambda y: y.product_id == product
                ) for product in products}
                extra_cost = 0.0
                extra_cost_invoice_lines = self.env["account.invoice.line"]
                # get extra cost for every group of invoice lines of an invoice for a
                # product
                for product in invoice_line_by_products:
                    invoice_cost = sum([
                        invoice_line.price_subtotal_signed for invoice_line in
                        invoice_line_by_products[product]
                    ])
                    raw_move_cost = - sum(
                        [
                            raw_move.price_unit * raw_move.quantity_done for raw_move in
                            raw_move_by_product[product]
                        ] if product in raw_move_by_product else [0.0]
                    )
                    if invoice_cost > raw_move_cost:
                        extra_cost += invoice_cost - raw_move_cost
                        extra_cost_invoice_lines |= invoice_line_by_products[product]
                # add extra cost for invoice lines without product
                extra_cost_no_product = sum(
                    x.price_subtotal_signed for x in no_product_invoice_lines
                    if x.account_id == line.general_account_id
                    or [0]
                )
                line.extra_cost = - (extra_cost + extra_cost_no_product)
                if extra_cost_invoice_lines:
                    line.extra_cost_invoice_line_ids = [
                        (6, 0, extra_cost_invoice_lines.ids)]
                else:
                    line.extra_cost_invoice_line_ids = False
            else:
                line.extra_cost = 0.0
                line.extra_cost_invoice_line_ids = False
