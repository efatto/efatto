# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def _active_hotel_folio_count(self):
        res = dict(map(lambda x: (x, 0), self.ids))
        for partner in self:
            res[partner.id] = len(
                filter(lambda x: x.state in ['draft', 'confirmed'],
                       partner.hotel_folio_ids))
        return res

    active_hotel_folio_count = fields.Integer(
        compute=_active_hotel_folio_count,
        string='# of Active Hotel Folio',
    )
    hotel_folio_ids = fields.One2many(
        'hotel.folio', 'partner_id',
        'Hotel Folio'
    )
