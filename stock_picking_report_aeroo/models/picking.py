# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp.osv import orm, fields


class stock_picking(orm.Model):
    _inherit = "stock.picking"
    _columns = {
        'visible_price': fields.boolean(
            'Prezzi Visibili sul DDT',
            help="Mettendo questo flag sul report DDT verranno riportati /n"
                 " i prezzi di vendita dell'ordine relativo")
    }
