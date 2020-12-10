# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp


class AccountAnalyticSal(models.Model):
    _name = 'account.analytic.sal'
    _description = 'Account Analytic SAL'
    _order = 'id ASC'

    @api.multi
    @api.depends('percent_toinvoice',
                 'account_analytic_id.total_sale',
                 'account_analytic_id.invoice_line_ids.price_subtotal',
                 'account_analytic_id.invoice_line_ids.invoice_id.state')
    def compute_invoiced_sal(self):
        for sal in self:
            for line in sal.account_analytic_id.invoice_line_ids.filtered(
                lambda x: x.account_analytic_sal_id == sal
            ):
                sal.amount_invoiced += line.price_subtotal
            sal.amount_toinvoice = \
                sal.account_analytic_id.total_sale * sal.percent_toinvoice / 100
            sal.residual_toinvoice = sal.amount_toinvoice - sal.amount_invoiced
            if sal.amount_invoiced >= sal.amount_toinvoice > 0.0:
                sal.invoiced = True

    name = fields.Char('SAL name')
    account_analytic_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Analytic account',
        ondelete='cascade',
        required=True
    )
    currency_id = fields.Many2one(
        related="account_analytic_id.currency_id",
        string="Currency",
        readonly=True)
    percent_completion = fields.Float(
        'SAL percent done',
        digits=dp.get_precision('Account')
    )
    percent_toinvoice = fields.Float(
        'SAL percent to invoice',
        digits=dp.get_precision('Account'))
    amount_toinvoice = fields.Monetary(
        'SAL amount to invoice',
        compute=compute_invoiced_sal,
        store=True)
    amount_invoiced = fields.Monetary(
        'SAL amount invoiced',
        compute=compute_invoiced_sal,
        store=True)
    residual_toinvoice = fields.Monetary(
        'SAL residual to invoice',
        compute=compute_invoiced_sal,
        store=True)
    done = fields.Boolean(
        string='SAL done',
        help='SAL is marked done when completion percent is superior'
             ' of account progress bar. It can be marked even manually.'
    )
    invoiced = fields.Boolean(
        string='SAL invoiced',
        compute=compute_invoiced_sal,
        help='SAL is marked invoiced when amount invoice lines with sal '
             'reference is superior '
             'of SAL amount. It can be marked even manually.'
    )
