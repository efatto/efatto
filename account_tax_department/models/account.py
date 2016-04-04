# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class AccountTaxDepartment(models.Model):
    _name = 'account.tax.department'
    _description = 'Tax department'

    name = fields.Char(
        'Tax Department description', size=32, required=True,
        help='The Description of the department')
    tax_department = fields.Integer(
        'Tax Department', required=True)


class AccountTax(models.Model):
    _inherit = 'account.tax'

    tax_department = fields.Many2one(
        'account.tax.department', string='Tax Department')
