# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    tax_code_is_base = fields.Boolean(
        string='Tax is base',
        related='tax_code_id.is_base',
        copy=False, store=False, readonly=True
        )
