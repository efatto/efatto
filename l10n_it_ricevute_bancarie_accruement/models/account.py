# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    invoice_number = fields.Char()
