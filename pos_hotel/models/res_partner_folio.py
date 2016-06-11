# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
# from openerp import models, fields, api, _
from openerp.osv import fields, osv


class ResPartner(osv.osv):
    _inherit = 'res.partner'

    def _active_hotel_folio_count(self, cr, uid, ids, field_name, arg, context=None):
        res = dict(map(lambda x: (x, 0), ids))
        # The current user may not have access rights for sale orders
        try:
            for partner in self.browse(cr, uid, ids, context):
                res[partner.id] = len(
                    filter(lambda x: x.state in ['draft', 'confirmed'],
                           partner.hotel_folio_ids))
        except:
            pass
        return res

    _columns = {
        'active_hotel_folio_count': fields.function(_active_hotel_folio_count,
                                                  string='# of Active Hotel Folio',
                                                  type='integer'),
        'hotel_folio_ids': fields.one2many('hotel.folio', 'partner_id',
                                          'Hotel Folio')
    }
