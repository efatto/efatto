# Copyright 2023 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def action_invoice_open(self):
        res = super().action_invoice_open()
        if not self:
            return res
        if self.type == 'in_invoice':
            product_invoice_line_ids = self.mapped('invoice_line_ids').filtered(
                lambda x: x.product_id
            )
            analytic_invoice_line_ids = self.mapped('invoice_line_ids').filtered(
                lambda x: x.product_id and x.account_analytic_id
            )
            # first update analytic, then others with or without analytic
            if analytic_invoice_line_ids:
                analytic_accounts = analytic_invoice_line_ids.mapped(
                    'account_analytic_id')
                invoice_lines = self.env['account.invoice.line'].search([
                    ('account_analytic_id', 'in', analytic_accounts.ids),
                    ('product_id', 'in', analytic_invoice_line_ids.mapped(
                        'product_id.id')),
                    ('invoice_type', '=', 'in_invoice'),
                ])
                invoice_lines |= analytic_invoice_line_ids
                if invoice_lines:
                    invoice_lines.account_stock_price_unit_sync()
            if product_invoice_line_ids:
                product_invoice_lines = self.env['account.invoice.line'].search([
                    ('product_id', 'in', product_invoice_line_ids.mapped(
                        'product_id.id')),
                    ('invoice_type', '=', 'in_invoice'),
                ])
                product_invoice_lines |= product_invoice_line_ids
                if product_invoice_lines:
                    product_invoice_lines.account_stock_price_unit_sync()
        return res


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    def _get_price_with_discount(self, price):
        price = price * (1 - self.discount / 100.0)
        if hasattr(self, 'discount2'):
            price = price * (1 - self.discount2 / 100.0)
            price = price * (1 - self.discount3 / 100.0)
        return price

    @api.multi
    def _get_invoice_line_price_unit(self):
        self.ensure_one()
        line = self[0]
        invoice = line.invoice_id
        price_unit = line._get_price_with_discount(line.price_unit)
        if line.invoice_line_tax_ids:
            price_unit = line.invoice_line_tax_ids.with_context(
                round=False
            ).compute_all(
                price_unit, currency=invoice.currency_id, quantity=1.0,
                product=line.product_id, partner=invoice.partner_id
            )['total_excluded']
        if line.uom_id.id != line.product_id.uom_id.id:
            price_unit *= line.uom_id.factor / line.product_id.uom_id.factor
        if invoice.currency_id != invoice.company_id.currency_id:
            price_unit = invoice.currency_id._convert(
                price_unit, invoice.company_id.currency_id,
                self.company_id, invoice.date or fields.Date.today(), round=False)
        return price_unit

    @api.multi
    def account_stock_price_unit_sync(self):
        # {product_id: {account_analytic_id: [invoice_lines]}}
        lines_grouped = {product: {} for product in self.mapped('product_id')}
        for product in lines_grouped:
            lines = self.filtered(lambda x: x.product_id == product)
            for analytic in lines.mapped('account_analytic_id'):
                lines_grouped[product].update({
                    analytic: lines.filtered(
                        lambda y: y.account_analytic_id == analytic
                    )
                })
            lines_grouped[product].update({
                False: lines
            })

        for product in lines_grouped:
            # todo a phantom bom is possible in account.invoice.line?
            # When the affected product is a kit we do nothing, which is the
            # default behavior on the standard: the move is exploded into moves
            # for the components and those get the default price_unit for the
            # time being. We avoid a hard dependency as well.
            if (
                hasattr(product, "bom_ids")
                and product._is_phantom_bom()
            ):
                continue
            for analytic in lines_grouped[product]:
                if analytic:
                    lines = lines_grouped[product][analytic]
                    if len(lines.mapped('uom_id')) > 1:
                        # todo group by different uom_id? or is it possible to compute?
                        continue
                    # compute an avg price on qty invoiced and put in price unit of
                    # stockmoves (without qty limit)
                    # e.g.: purchase 18 pz at 188€ each and 10 pz at 265€ each, for a
                    # total of 28 pz and 6.034,00€ at an average price of 215,50€
                    # so put 215,50€ in unit price of stock moves
                    total_qty = sum(lines.mapped('quantity'))
                    avg_price_unit = [
                        line.quantity * line._get_invoice_line_price_unit()
                        for line in lines]
                    if avg_price_unit:
                        avg_price_unit = sum(avg_price_unit) / (total_qty or 1)
                    else:
                        continue
                    # search without date nor state as they are unpredictable
                    # stock move from sales or productions
                    used_move_ids = self.env['stock.move'].search([
                        ('product_id', '=', product.id),
                        ('location_dest_id.usage', 'in', ['production', 'customer']),
                        '|',
                        ('sale_line_id.order_id.analytic_account_id', '=', analytic.id),
                        ('raw_material_production_id.analytic_account_id', '=',
                         analytic.id)
                    ])
                    used_move_ids.write({
                        'is_analytic_synced': True,
                        'price_unit': - avg_price_unit,
                    })
                else:
                    # update stock moves residual from analytic search
                    # stock move from sales or productions
                    # before invoice lines to get price by date incoming move
                    invoice_lines = lines_grouped[product][False]
                    used_moves = self.env['stock.move'].search([
                        ('is_analytic_synced', '=', False),
                        ('product_id', '=', product.id),
                        ('location_dest_id.usage', 'in', ['production', 'customer']),
                        '|',
                        ('sale_line_id.order_id.analytic_account_id', '!=', False),
                        ('raw_material_production_id.analytic_account_id', '!=', False),
                    ])
                    for used_move in used_moves:
                        # get best invoice line for price
                        moved_purchase_invoice_lines = invoice_lines.filtered(
                            lambda x: x.purchase_line_id.move_ids
                        )
                        if moved_purchase_invoice_lines:
                            lines = moved_purchase_invoice_lines.filtered(
                                lambda x: x.purchase_line_id.mapped(
                                    'move_ids.date'
                                )[0] <= used_move.date
                            )
                            if lines:
                                line = lines.sorted(
                                    key=lambda y: y.purchase_line_id.mapped(
                                        'move_ids.date'),
                                    reverse=True
                                )[0]
                                price_unit = line._get_invoice_line_price_unit()
                                used_move.write({
                                    'price_unit': - price_unit,
                                })
