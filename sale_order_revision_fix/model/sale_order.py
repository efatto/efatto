# -*- coding: utf-8 -*-
from openerp import models, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def copy_quotation(self):
        self.ensure_one()
        res = super(SaleOrder, self).copy_quotation()
        self.old_revision_ids.order_line.write({'state': 'cancel'})
        return res
