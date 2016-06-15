# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    abi = fields.Char(
            related='partner_id.bank_riba_id.abi', string='ABI',
            store=False)
    cab = fields.Char(
            related='partner_id.bank_riba_id.cab', string='CAB',
            store=False)
