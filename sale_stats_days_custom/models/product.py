# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from odoo.tools.float_utils import float_round
from datetime import timedelta, time


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def _compute_sales_count(self):
        r = super()._compute_sales_count()
        if not self.user_has_groups('sales_team.group_sale_salesman'):
            return r
        days = 365
        if self.company_id.sale_stat_days:
            days = self.company_id.sale_stat_days
        date_from = fields.Datetime.to_string(fields.datetime.combine(
            fields.datetime.now() - timedelta(days=days), time.min))

        done_states = self.env['sale.report']._get_done_states()

        domain = [
            ('state', 'in', done_states),
            ('product_id', 'in', self.ids),
            ('date', '>=', date_from),
        ]
        for group in self.env['sale.report'].read_group(
                domain, ['product_id', 'product_uom_qty'], ['product_id']):
            r[group['product_id'][0]] = group['product_uom_qty']
        for product in self:
            product.sales_count = float_round(
                r.get(product.id, 0), precision_rounding=product.uom_id.rounding)
        return r
