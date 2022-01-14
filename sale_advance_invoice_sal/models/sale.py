# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    @api.model
    def _get_orders(self):
        sale_orders = self.env['sale.order'].browse(
            self._context.get('active_ids', []))
        return sale_orders

    @api.model
    def _get_analytic_account_ids(self):
        analytic_ids = self.env['sale.order'].browse(
            self.order_ids).mapped('analytic_account_id')
        return analytic_ids

    @api.onchange('sal_id')
    def _get_sal_percent(self):
        if self._count() == 1:
            if self.sal_id:
                self.amount = self.sal_id.percent_toinvoice

    order_ids = fields.Many2many(
        comodel_name='sale.order',
        default=_get_orders,
    )
    analytic_account_ids = fields.Many2many(
        comodel_name='account.analytic.account',
        default=_get_analytic_account_ids,
    )
    sal_id = fields.Many2one(
        comodel_name='account.analytic.sal',
        string='SAL',
        help='Select sal line to link to invoice line'
    )

    @api.multi
    def _create_invoice(self, order, so_line, amount):
        invoice = super(SaleAdvancePaymentInv, self)._create_invoice(
            order, so_line, amount)
        if self.sal_id:
            for invoice_line in invoice.invoice_line_ids:
                invoice_line.account_analytic_sal_id = self.sal_id
        return invoice
