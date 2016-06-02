# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class AccountMoveTemplateLine(models.Model):
    _inherit = 'account.move.template.line'

    amount = fields.Float(string="Fixed Amount")
    type = fields.Selection(
        [('computed', 'Computed'), ('input', 'User input'),
         ('amount', 'Fixed amount')],
        string='Type',
        required=True
    )
