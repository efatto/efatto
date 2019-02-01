# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
import odoo.addons.decimal_precision as dp


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'
    #
    # @api.multi
    # def get_account_hours_quantity(self):
    #     for account in self:
    #         account.hours_quantity = sum(account.task_ids.hours)
    #
    #
    # @api.multi
    # def get_progress(self):
    #     for account in self:
    #         account.progress_works_planned = 0.0
    #         if account.quantity and account.hours_quantity:
    #             account.progress_works_planned = \
    #                 account.hours_quantity / account.quantity * 100

    @api.multi
    def _get_amount_sal_to_invoice(self):
        for account in self:
            total = 0.0
            for sal in account.account_analytic_sal_ids:
                if sal.done or sal.percent_completion > 0.0:
                    # account.progress_works_planned >
                    # and not sal.invoiced:
                    total += sal.amount_toinvoice
                    total -= sal.amount_invoiced
            account.amount_sal_to_invoice += total

    # FIX amount_fix_price is always the total from orders, even if invoiced
    @api.multi
    def fix_price_to_invoice_calc(self):
        sale_obj = self.env['sale.order']
        for account in self:
            total = 0.0
            sale_ids = sale_obj.search([
                ('project_id', '=', account.id),
                ('state', 'not in', ['draft', 'sent', 'cancel']) #'manual')
            ])
            for sale in sale_ids:
                total += sale.amount_untaxed
            account.fix_price_to_invoice = total

    @api.multi
    def ca_invoiced_calc(self):
        invoice_line_obj = self.env['account.invoice.line']
        for account in self:
            total = 0.0
            line_ids = invoice_line_obj.search([
                ('account_analytic_id', '=', account.id),
                ('invoice_id.state', 'not in',
                    ['draft', 'sent', 'cancel']) #'manual')
            ])
            for line in line_ids:
                total += line.price_subtotal
            account.fix_price_to_invoice = total

    @api.multi
    def remaining_ca_calc(self):
        for account in self:
            account.remaining_ca = \
                max(account.amount_max, account.fix_price_to_invoice) \
                - account.ca_invoiced

    use_sal = fields.Boolean(
        string='Use SAL'
    )
    ca_invoiced = fields.Float(
        compute='ca_invoiced_calc',
        string='Invoiced amount',
        digits_compute=dp.get_precision('Account')
    )
    amount_max = fields.Float(
        string='Account Amount Max',
        digits_compute=dp.get_precision('Account')
    )
    remaining_ca = fields.Float(
        compute='remaining_ca_calc',
        string='Remaining Revenue',
        help="Computed using the formula: Max Invoice Price - Invoiced Amount",
        digits_compute=dp.get_precision('Account')
    )
    fix_price_to_invoice = fields.Float(
        compute='fix_price_to_invoice_calc',
        string='Total Fix Price',
        help="Sum of quotations for this contract.")
    # progress_works_planned = fields.Float(
    #     help='Progress on hours planned on contract',
    #     compute='get_progress')
    account_analytic_sal_ids = fields.One2many(
        comodel_name='account.analytic.sal',
        inverse_name='account_analytic_id',
        string='Analytic SAL progression'
    )
    amount_sal_to_invoice = fields.Float(
        compute='_get_amount_sal_to_invoice',
        help='Amount to invoice from SAL',
    )


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
    def get_invoiced_sal(self):
        for sal in self:
            amount_invoiced = 0.0
            account_invoice_line_ids = self.env['account.invoice.line'].search(
                [('account_analytic_sal_id', '=', sal.id)])
            for line in account_invoice_line_ids:
                if line.invoice_id.state in ['open', 'done']:
                    amount_invoiced += line.price_subtotal
            if amount_invoiced >= sal.amount_toinvoice > 0.0:
                sal.invoiced = True
            # set automatically sal done when progress>sal percent completion
            if sal.percent_completion > 0.0:
                #sal.account_analytic_id.progress_works_planned >
                sal.done = True
            sal.amount_invoiced = amount_invoiced

    @api.multi
    def _compute_amount_toinvoice(self):
        for sal in self:
            sal.amount_toinvoice = sal.account_analytic_id.\
                fix_price_to_invoice * sal.percent_toinvoice / 100

    name = fields.Char('SAL name')
    percent_completion = fields.Float(
        'SAL percent completion',
        digits_compute=dp.get_precision('Account'),
        help='Percent SAL completion. When reached will start action linked.'
    )
    percent_toinvoice = fields.Float(
        'SAL percent to invoice',
        digits_compute=dp.get_precision('Account'))
    amount_toinvoice = fields.Float(
        'SAL amount to invoice',
        compute='_compute_amount_toinvoice',
        digits_compute=dp.get_precision('Account'))
    amount_invoiced = fields.Float(
        'SAL amount invoiced',
        compute='get_invoiced_sal',
        digits_compute=dp.get_precision('Account'))
    done = fields.Boolean(
        string='SAL done',
        help='SAL is marked done when completion percent is superior'
             ' of account progress bar. It can be marked even manually.'
    )
    invoiced = fields.Boolean(
        string='SAL invoiced',
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
    action_id = fields.Many2one(
        comodel_name='ir.actions.server',
        string='Server Action to do',
        help='This action will be done on SAL condition if not already done.'
    )
    action_res_model_id = fields.Char(
        string='Related Model for server action done by the event',
        readonly=True
    )
    action_res_id = fields.Integer(
        string='Related ID for server action done by the event',
        readonly=True
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
