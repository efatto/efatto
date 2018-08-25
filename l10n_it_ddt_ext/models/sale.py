# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from odoo import fields, models, api, _, exceptions


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

    def _preparare_ddt_data(self):
        res = super(SaleOrder, self)._preparare_ddt_data()
        ddt_type = self.ddt_type_id
        if not res.get('carriage_condition_id', False):
            res['carriage_condition_id'] = \
                ddt_type.default_carriage_condition_id.id
        if not res.get('goods_description_id', False):
            res['goods_description_id'] = \
                ddt_type.default_goods_description_id.id
        if not res.get('transportation_reason_id', False):
            res['transportation_reason_id'] = \
                ddt_type.default_transportation_reason_id.id
        if not res.get('transportation_method_id', False):
            res['transportation_method_id'] = \
                ddt_type.default_transportation_method_id.id
        if not res.get('ddt_type_id', False):
            res['ddt_type_id'] = self.ddt_type_id.id
        return res

    @api.multi
    def action_cancel(self):
        for order in self:
            for ddt in order.ddt_ids:
                if ddt.state in ['done', 'in_pack']:
                    raise exceptions.Warning(_(
                        'DDT is already done or in pack.'))
                for picking in ddt.picking_ids:
                    if picking.state in ['done', 'in_pack']:
                        raise exceptions.Warning(
                            _('Picking is already done or in pack.'))
                # all pickings are cancelled, so remove ddt
                ddt.unlink()
                # todo if ddt had a number because it was put in pack and then
                # todo cancelled, the sequence will have a hole
        return super(SaleOrder, self).action_cancel()
