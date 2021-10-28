# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api, _


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    @api.model
    def _get_order_lines(self):
        line_ids = self.env['sale.order'].browse(
            self._context['active_id']).order_line
        return line_ids

    order_line_ids = fields.Many2many(
        comodel_name='sale.order.line',
        relation='advance_sale_order_line_rel',
        column1='order_line_id', column2='advance_id',
        string='Order lines',
        default=_get_order_lines,
        help='Select order lines to print details in invoice'
    )

    @api.multi
    def _create_invoice(self, order, so_line, amount):
        invoice = super(SaleAdvancePaymentInv, self)._create_invoice(
            order, so_line, amount)
        if self.advance_payment_method in ('fixed', 'percentage') \
                and self.order_line_ids:
            description = '\n'.join(self.order_line_ids.mapped('name'))
            for invoice_line in invoice.invoice_line_ids:
                invoice_line.name = '%s \n%s' % (invoice_line.name, description)
        return invoice
