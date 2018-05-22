# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models


class AccountMove(models.Model):
    _inherit = 'account.move'

    _sql_constraints = [(
        'name_account_move_uniq',
        'unique(name, company_id)',
        'An account move with the same name already exists for this company!'
        )]
