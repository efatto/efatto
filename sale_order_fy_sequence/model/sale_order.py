# -*- coding: utf-8 -*-
from openerp import models, api, fields


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def create(self, values):
        if not self.env.context.get('fiscalyear_id'):
            if values.get('name', '/') == '/' and values.get('date_order'):
                date_order = values['date_order']
                fy_id = self.env['account.fiscalyear'].find(
                    dt=fields.Datetime.from_string(date_order))
                seq = self.env['ir.sequence']
                values['name'] = seq.with_context(
                    {'fiscalyear_id': fy_id}).next_by_code('sale.order') or '/'
        return super(SaleOrder, self).create(values)

# package.ddt_type_id.sequence_id.\
#                     with_context({'fiscalyear_id': fy_id}).get(
#                         package.ddt_type_id.sequence_id.code)