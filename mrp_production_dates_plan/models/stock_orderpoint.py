from odoo import api, fields, models,  _


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    def _get_product_context(self):
        res = super()._get_product_context()
        # remove to_date from context as all future incoming qty has to be considered
        res.update({
            'to_date': None,
            # original: datetime.combine(self.lead_days_date, time.max)
        })
        return res
