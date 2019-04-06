# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from odoo import models, fields, api, _


class AccountJournal(models.Model):
    _inherit = 'account.journal'
    _order = 'sequence'

    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Sequence used to order account journal')
