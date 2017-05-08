# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, exceptions
import openerp.addons.decimal_precision as dp


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.multi
    def get_progress(self):
        progress = 0.0
        for project in self:
            if project.quantity_max and project.hours_quantity:
                progress = project.hours_quantity / project.quantity_max * 100
            project.progress_works_planned = progress

    progress_works_planned = fields.Float(
        help='Progress on hours planned on contract',
        compute='get_progress')
    account_analytic_sal_ids = fields.One2many(
        comodel_name='account.analytic.sal',
        inverse_name='account_analytic_id',
        string='Analytic SAL progression'
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
            if sal.account_analytic_id.progress_works_planned > \
                    sal.percent_completion > 0.0:
                sal.done = True
            sal.amount_invoiced = amount_invoiced

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
        digits_compute=dp.get_precision('Account'))
    amount_invoiced = fields.Float(
        'SAL amount invoiced',
        compute='get_invoiced_sal',
        digits_compute=dp.get_precision('Account'))
    done = fields.Boolean(
        string='SAL done',
        help='SAL is marked done when completion percent is superior'
             ' of project progress bar. It can be marked even manually.'
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
        help='This action will be done on SAL condition if not done.'
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
