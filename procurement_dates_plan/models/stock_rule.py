from odoo import fields, models
from odoo.tools.date_utils import relativedelta


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _prepare_purchase_order(self, company_id, origins, values):
        res = super()._prepare_purchase_order(
            company_id=company_id, origins=origins, values=values)
        purchase_date = min(
            [
                fields.Datetime.from_string(value['date_planned'])
                - relativedelta(days=int(value['supplier'].delay)) for value in values
            ]
        )
        res.update(date_order=purchase_date)
        return res
