from odoo import models, fields


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    abi = fields.Char(
        related='partner_id.bank_riba_id.abi', string='ABI',
        store=False)
    cab = fields.Char(
        related='partner_id.bank_riba_id.cab', string='CAB',
        store=False)
