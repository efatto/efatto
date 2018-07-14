# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import fields, api, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    task_count = fields.Integer(related='partner_id.task_count')

    # def _crm_task_count(self, cr, uid, ids, field_name, arg, context=None):
    #     res = super(res_partner, self)._sale_order_count(cr, uid, ids, field_name=field_name, arg=arg, context=context)
    #     # The current user may not have access rights for sale orders
    #     try:
    #         for partner in self.browse(cr, uid, ids, context):
    #             res[partner.id] = len(filter(lambda x: x.state not in ['draft', 'sent', 'cancel'], partner.sale_order_ids)) \
    #                               + len(partner.mapped(
    #                               'child_ids.sale_order_ids'))
    #     except:
    #         pass
    #     return res
    #
    # def _draft_sale_order_count(self, cr, uid, ids, field_name, arg, context=None):
    #     res = dict(map(lambda x: (x,0), ids))
    #     # The current user may not have access rights for sale orders
    #     try:
    #         for partner in self.browse(cr, uid, ids, context):
    #             res[partner.id] = len(filter(lambda x: x.state in ['draft', 'sent', 'cancel'], partner.sale_order_ids)) \
    #                               + len(partner.mapped(
    #                               'child_ids.sale_order_ids'))
    #     except:
    #         pass
    #     return res
    #
    # _columns = {
    #     'sale_order_count': fields.function(_sale_order_count,
    #                                         string='# of Sales Order',
    #                                         type='integer'),
    #     'draft_sale_order_count': fields.function(_draft_sale_order_count,
    #                                         string='# of Draft Sales Order',
    #                                         type='integer'),
    #     'sale_order_ids': fields.one2many('sale.order','partner_id',
    #                                       'Sales Order')
    # }
