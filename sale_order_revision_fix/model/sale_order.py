# -*- coding: utf-8 -*-
from openerp import models, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def copy_quotation(self):
        self.ensure_one()
        res = super(SaleOrder, self).copy_quotation()
        for old_revision in self.old_revision_ids:
            old_revision.order_line.write({'state': 'cancel'})
        return res

    @api.multi
    def copy(self, default=None):
        if default is None:
            default = {}
        if self.env.context.get('new_sale_revision'):
            self.write({'procurement_group_id': False})
        return super(SaleOrder, self).copy(default=default)
