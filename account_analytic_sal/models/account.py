# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api
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

# class HrAnalyticTimesheet(models.Model):
#     _inherit = 'hr.analytic.timesheet'
#
#     @api.multi
#     def write(self, vals):
#         # when updating, do action if account id has sal
#         for timesheet in self.filtered(
#                 lambda x: x.account_id.account_analytic_sal_ids is not False):
#             contract = timesheet.account_id
#             for sal_id in contract.account_analytic_sal_ids.filtered(
#                     lambda x: x.sal_action_res_id is not True
#             ):
#                 if contract.progress_works_planned >= sal_id.sal_percent:
#                     sal_action_done_id = sal_id.sal_action_id.with_context({
#                         'partner_id': contract.partner_id.id,
#                         'active_id': contract.id,
#                         'active_ids': [contract.id],
#                         }).run()
#                     if sal_action_done_id:
#                         sal_id.sal_action_res_id = sal_action_done_id
#                         sal_id.sal_action_res_model_id = sal_id.sal_action_id.\
#                             model_id.name
#         return super(HrAnalyticTimesheet, self).write(vals)


class AccountAnalyticSal(models.Model):
    _name = 'account.analytic.sal'
    _description = 'Account Analytic SAL'

    @api.multi
    def get_invoiced_sal(self):
        for sal in self:
            amount_invoiced = 0.0
            account_invoice_line_ids = self.env['account.invoice.line'].search(
                [('account_analytic_sal_id', '=', sal.id)])
            for line in account_invoice_line_ids:
                if line.invoice_id.state in ['open','done']:
                    amount_invoiced += line.price_subtotal
            if amount_invoiced >= sal.amount_toinvoice:
                sal.invoiced = True
            if sal.percent_completion >= sal.percent_toinvoice:
                sal.done = True
            sal.amount_invoiced = amount_invoiced

    name = fields.Char('SAL name')
    percent_completion = fields.Float(
        'SAL percent completion',
        digits_compute=dp.get_precision('Account'))
    percent_toinvoice = fields.Float(
        'SAL percent to invoce',
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
             ' of SAL percent. It can be marked even manually.'
    )
    invoiced = fields.Boolean(
        string='SAL invoiced',
        help='SAL is marked invoiced when amount invoice lines is superior'
             ' of SAL amount. It can be marked even manually.'
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
