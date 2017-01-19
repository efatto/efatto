# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    note= fields.Text(translate=True)
