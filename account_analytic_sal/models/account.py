# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, exceptions, _
import odoo.addons.decimal_precision as dp


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    account_analytic_sal_id = fields.Many2one(
        comodel_name='account.analytic.sal',
        string='Analytic SAL',
        help='SAL linked to this line'
    )


class AccountAnalyticSal(models.Model):
    _name = 'account.analytic.sal'
    _description = 'Account Analytic SAL'
    _order = 'id ASC'

    @api.multi
    @api.depends('account_analytic_id.invoice_line_ids.price_subtotal',
                 'account_analytic_id.invoice_line_ids.invoice_id.state',
                 'account_analytic_id.total_sale', 'percent_toinvoice')
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
    percent_completion = fields.Float(
        'SAL percent done',
        digits=dp.get_precision('Account')
    )
    percent_toinvoice = fields.Float(
        'SAL percent to invoice',
        digits=dp.get_precision('Account'))
    amount_toinvoice = fields.Float(
        'SAL amount to invoice',
        compute=compute_invoiced_sal,
        store=True,
        digits=dp.get_precision('Account'))
    amount_invoiced = fields.Float(
        'SAL amount invoiced',
        compute=compute_invoiced_sal,
        store=True,
        digits=dp.get_precision('Account'))
    residual_toinvoice = fields.Float(
        'SAL residual to invoice',
        compute=compute_invoiced_sal,
        store=True,
        digits=dp.get_precision('Account'))
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
    account_analytic_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Analytic account',
        ondelete='cascade',
        required=True
    )

    @api.multi
    @api.constrains('percent_toinvoice')
    def _check_percent_toinvoice(self):
        percent_toinvoice_total = 0.0
        for sal in self.account_analytic_id.account_analytic_sal_ids:
            percent_toinvoice_total += sal.percent_toinvoice
        if percent_toinvoice_total > 100.0:
            raise exceptions.ValidationError(
                "SAL total % to invoice must be <= 100%")
