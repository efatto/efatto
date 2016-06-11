# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.one
    def _get_folio_id(self):
        self.folio_id = False
        self.room_id = False
        folio_ids = self.env['hotel.folio'].search(
            [('state', 'not in', ['draft', 'sent', 'cancel', 'done']),
             ('partner_id', '=', self.id),
             ('checkin_date', '<=', fields.Datetime.now()),
             ('checkout_date', '>=', fields.Datetime.now()),
             ])
        if folio_ids:
            self.folio_id = folio_ids[0].id
            if folio_ids[0].room_lines:
                self.room_id = folio_ids[0].room_lines[0].product_id.id

    folio_id = fields.Many2one(
        comodel_name='hotel.folio',
        compute='_get_folio_id',
        store=False, string='Folio',
    )
    room_id = fields.Many2one(
        comodel_name='product.product',
        compute='_get_folio_id',
        store=False, string='Room',
    )

