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


class HrAnalyticTimesheet(models.Model):
    _inherit = 'hr.analytic.timesheet'

    @api.multi
    def write(self, vals):
        # when updating, do action if account id has sal
        for timesheet in self.filtered(
                lambda x: x.account_id.account_analytic_sal_ids is not False):
            contract = timesheet.account_id
            for sal_id in contract.account_analytic_sal_ids.filtered(
                    lambda x: x.sal_action_res_id is not True
            ):
                if contract.progress_works_planned >= sal_id.sal_percent:
                    sal_action_done_id = sal_id.sal_action_id.with_context({
                        'partner_id': contract.partner_id.id,
                        'active_id': contract.id,
                        'active_ids': [contract.id],
                        }).run()
                    if sal_action_done_id:
                        sal_id.sal_action_res_id = sal_action_done_id
                        sal_id.sal_action_res_model_id = sal_id.sal_action_id.\
                            model_id.name
        return super(HrAnalyticTimesheet, self).write(vals)


class AccountAnalyticSal(models.Model):
    _name = 'account.analytic.sal'
    _description = 'Account Analytic SAL'

    name = fields.Char('SAL name')
    sal_percent = fields.Float(
        'SAL percent', required=True,
        digits_compute=dp.get_precision('Account'))
    account_analytic_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Analytic account',
        ondelete='cascade',
        required=True
    )
    sal_action_id = fields.Many2one(
        comodel_name='ir.actions.server',
        string='Server Action to do',
        help='This action will be done on SAL condition if not done.'
    )
    sal_action_res_model_id = fields.Char(
        string='Related Model for server action done by the event'
    )
    sal_action_res_id = fields.Integer(
        string='Related ID for server action done by the event'
    )
