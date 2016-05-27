# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import fields, models, api


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    @api.model
    def default_get(self, fields):
        res = super(SaleOrder, self).default_get(fields)
        if res:
            company = self.env.user.company_id
            res['create_ddt'] = company.create_ddt \
                    if company.create_ddt \
                    else False
        return res

    def _default_ddt_type(self):
        return self.env['stock.ddt.type'].search([], limit=1)

    ddt_type_id = fields.Many2one(
        'stock.ddt.type',
        'Type of DDT', default=_default_ddt_type)

    def _preparare_ddt_data(self, cr, uid, order, context=None):
        res = super(SaleOrder, self)._preparare_ddt_data(
            cr, uid, order, context)
        ddt_type = order.ddt_type_id
        if not res.get('carriage_condition_id', False):
            res['carriage_condition_id'] = ddt_type.carriage_condition_id.id
        if not res.get('goods_description_id', False):
            res['goods_description_id'] = ddt_type.goods_description_id.id
        if not res.get('transportation_reason_id', False):
            res['transportation_reason_id'] = \
                ddt_type.transportation_reason_id.id
        if not res.get('transportation_method_id', False):
            res['transportation_method_id'] = \
                ddt_type.transportation_method_id.id
        if not res.get('ddt_type_id', False):
            res['ddt_type_id'] = ddt_type.id
        return res
