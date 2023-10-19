# Copyright 2023 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _prepare_purchase_order(self, company_id, origins, values):
        res = super()._prepare_purchase_order(company_id, origins, values)
        # purchase_date = min(
        #     [fields.Datetime.from_string(value['date_planned'])
        #         - relativedelta(days=int(value['supplier'].delay)) for value in values]
        # )
        #
        # purchase_date = (purchase_date - relativedelta(days=company_id.po_lead))
        return res
