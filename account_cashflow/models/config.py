# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    cashflow_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Account for cash flow temporary moves',
        )


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    cashflow_account_id = fields.Many2one(
        string="Account for cash flow temporary moves",
        related='company_id.cashflow_account_id')
