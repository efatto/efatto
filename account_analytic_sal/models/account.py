# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
import odoo.addons.decimal_precision as dp


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.multi
    def get_progress(self):
        for account in self:
            account.progress_hours = 0.0
            if account.hours_done and account.hours_planned:
                account.progress_hours = \
                    account.hours_done / account.hours_planned * 100

    @api.multi
    def _compute_done_hours(self):
        analytic_line_model = self.env['account.analytic.line']
        for analytic in self:
            fetch_data = analytic_line_model.read_group(
                [('project_id', 'in', analytic.project_ids.ids)],
                ['unit_amount'], [],
            )
            analytic.hours_done = fetch_data[0]['unit_amount']

    @api.multi
    def _compute_planned_hours(self):
        sale_line_model = self.env['sale.order.line']
        time_type_id = self.env.ref('product.uom_categ_wtime')
        for analytic in self:
            fetch_data = sale_line_model.read_group(
                [('order_id.project_id', '=', analytic.id),
                 ('product_uom.category_id', '=', time_type_id.id),
                 ('order_id.state', 'not in', ['draft', 'sent', 'cancel'])],
                ['product_uom_qty', 'product_uom'], ['product_uom'],
            )
            hours_planned = 0.0
            for d in fetch_data:
                if not d['product_uom_qty']:
                    continue
                # get total hours planned
                uom = self.env.ref('product.product_uom_hour')
                uom_base = self.env['product.uom'].browse(d['product_uom'][0])
                hours_planned += uom_base._compute_quantity(
                    d['product_uom_qty'], uom)
            analytic.hours_planned = hours_planned

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

    @api.multi
    def _get_amount_remaining(self):
        for account in self:
            account.amount_remaining = \
                account.total_sale - account.total_invoiced

    use_sal = fields.Boolean(
        string='Use SAL')
    fix_price_to_invoice = fields.Float(
        string='Contract Fix Amount',
        digits=dp.get_precision('Account'))
    amount_remaining = fields.Float(
        compute='_get_amount_remaining',
        string='Remaining Revenue',
        help="Computed using the formula: Sale Amount - Invoiced Amount",
        digits=dp.get_precision('Account'))
    hours_planned = fields.Float(
        string="Planned Hours",
        compute='_compute_planned_hours')
    hours_done = fields.Float(
        string="Done Hours",
        compute='_compute_done_hours')
    progress_hours = fields.Float(
        help='Progress on hours planned on contract',
        compute='get_progress')
    account_analytic_sal_ids = fields.One2many(
        comodel_name='account.analytic.sal',
        inverse_name='account_analytic_id',
        string='Analytic SAL progression')
    amount_sal_to_invoice = fields.Float(
        compute='_get_amount_sal_to_invoice',
        help='Amount to invoice from SAL')
    manager_id = fields.Many2one(
        'res.users', 'Account Manager', track_visibility='onchange')
    date_end = fields.Date(
        'End Date')


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
                total_sale * sal.percent_toinvoice / 100

    name = fields.Char('SAL name')
    percent_completion = fields.Float(
        'SAL percent completion',
        digits=dp.get_precision('Account'),
        help='Percent SAL completion. When reached will start action linked.'
    )
    percent_toinvoice = fields.Float(
        'SAL percent to invoice',
        digits=dp.get_precision('Account'))
    amount_toinvoice = fields.Float(
        'SAL amount to invoice',
        compute='_compute_amount_toinvoice',
        digits=dp.get_precision('Account'))
    amount_invoiced = fields.Float(
        'SAL amount invoiced',
        compute='get_invoiced_sal',
        digits=dp.get_precision('Account'))
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
