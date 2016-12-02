# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _preparare_ddt_data(self, order):
        res = super(SaleOrder, self)._preparare_ddt_data(order)
        res.update({'compute_weight': order.compute_weight,
                    'weight_custom': order.weight_custom,
                    'net_weight_custom': order.net_weight_custom,
                    'volume_custom': order.volume_custom,
                    })
        return res
