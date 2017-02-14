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


class AccountAnalyticSal(models.Model):
    _name = 'account.analytic.sal'
    _description = 'Account Analytic SAL'

    name = fields.Char('SAL name')
    sal_percent = fields.Float(
        'SAL percent', required=True,
        digits_compute=dp.get_precision('Account'))
    sal_done = fields.Boolean('SAL done')
    account_analytic_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Analytic account',
        ondelete='cascade',
        required=True
    )
