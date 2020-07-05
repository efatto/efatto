from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    res_partner_history_ids = fields.One2many(
        comodel_name='res.partner.history',
        inverse_name='partner_id',
        string='Partner history'
    )
