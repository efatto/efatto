# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import time, timedelta

from odoo import api, fields, models
from odoo.tools.float_utils import float_round


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _compute_sales_count(self):
        r = super()._compute_sales_count()
        if not self.user_has_groups("sales_team.group_sale_salesman"):
            return r
        days = 365
        if self.env.company.sale_stat_days:
            days = self.env.company.sale_stat_days
        date_from = fields.Datetime.to_string(
            fields.datetime.combine(
                fields.datetime.now() - timedelta(days=days), time.min
            )
        )

        done_states = self.env["sale.report"]._get_done_states()

        domain = [
            ("state", "in", done_states),
            ("product_id", "in", self.ids),
            ("date", ">=", date_from),
        ]
        for group in self.env["sale.report"].read_group(
            domain, ["product_id", "product_uom_qty"], ["product_id"]
        ):
            r[group["product_id"][0]] = group["product_uom_qty"]
        for product in self:
            if not product.id:
                product.sales_count = 0.0
                continue
            product.sales_count = float_round(
                r.get(product.id, 0), precision_rounding=product.uom_id.rounding
            )
        return r
