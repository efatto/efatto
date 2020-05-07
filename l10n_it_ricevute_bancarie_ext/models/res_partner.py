from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # this field is created even in account_bank, created also here to remove dependency
    bank_riba_id = fields.Many2one(
        'res.bank',
        'Bank for ri.ba.',
        help='If not filled, it will be used the first bank of the partner')
