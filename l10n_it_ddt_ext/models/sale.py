# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import fields, models, api, _, exceptions


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    @api.model
    def default_get(self, fields):
        res = super(SaleOrder, self).default_get(fields)
        if res:
            company = self.env.user.company_id
            res['create_ddt'] = company.create_ddt \
                if company.create_ddt else False
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
        if not res.get('parcels', False):
            res['parcels'] = order.parcels
        return res

    @api.multi
    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        for ddt in self.ddt_ids:
            if ddt.state not in ['cancel', 'draft']:
                raise exceptions.Warning(_('DDT is already done or in pack.'))
            for picking in ddt.picking_ids:
                if picking.state not in ['cancel', 'draft']:
                    raise exceptions.Warning(
                        _('Picking is not in draft or cancel state.'))
                picking.unlink()
            ddt.unlink()
        return res

    @api.multi
    def action_view_ddt(self):
        res = super(SaleOrder, self).action_view_ddt()
        for so in self:
            if len(so.ddt_ids) == 0:
                res['context'] = {'default_partner_id': so.partner_id.id,
                                  'default_ddt_type_id': so.ddt_type_id.id}
                if so.goods_description_id:
                    res['context'].update(
                        goods_description_id=so.goods_description_id.id)
                if so.carriage_condition_id:
                    res['context'].update(
                        carriage_condition_id=so.carriage_condition_id.id)
                if so.transportation_reason_id:
                    res['context'].update(transportation_reason_id=
                                          so.transportation_reason_id.id)
                if so.transportation_method_id:
                    res['context'].update(transportation_method_id=
                                          so.transportation_method_id.id)
        return res
