from odoo import models, fields, api, _


class RibaList(models.Model):
    _inherit = 'riba.distinta'
    _order = 'date_created DESC'

    line_ids = fields.One2many(
        readonly=False,
        states={'paid': [('readonly', True)],
                'cancel': [('readonly', True)]})

