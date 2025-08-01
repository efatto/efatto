from odoo import models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def action_invoice_open(self):
        res = super().action_invoice_open()
        if not self:
            return res
        if self.type == 'in_invoice':
            # Get all invoice lines with a product and retrieve all the invoice lines
            # from other invoices with these products to update stock prices.
            product_invoice_line_ids = self.mapped('invoice_line_ids').filtered(
                lambda x: x.product_id
            )
            if product_invoice_line_ids:
                product_invoice_lines = self.env['account.invoice.line'].search([
                    ('product_id', 'in', product_invoice_line_ids.mapped(
                        'product_id.id')),
                    ('invoice_type', '=', 'in_invoice'),
                    ('exclude_extra_cost', '=', False),
                ])
                product_invoice_lines |= product_invoice_line_ids
                if product_invoice_lines:
                    product_invoice_lines.account_stock_price_unit_sync()
        return res
