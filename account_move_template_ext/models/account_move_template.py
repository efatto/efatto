# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class AccountMoveTemplate(models.Model):
    _inherit = 'account.move.template'

    journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Default journal'
    )


class AccountMoveTemplateLine(models.Model):
    _inherit = 'account.move.template.line'

    amount = fields.Float(string="Fixed Amount")
    type = fields.Selection(
        [('computed', 'Computed'), ('input', 'User input'),
         ('amount', 'Fixed amount')],
        string='Type',
        required=True
    )
