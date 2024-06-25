from odoo import fields, models
from odoo.tools.date_utils import relativedelta


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _get_date_planned(self, product_id, company_id, values):
        super()._get_date_planned(product_id, company_id, values)
        date_requested = fields.Date.context_today(self)
        if values.get("date_planned", False) and not values.get("orderpoint_id", False):
            # not sure when this happens, sold MTO products perhaps
            date_requested = fields.Date.from_string(values["date_planned"])
        avail_date, avail_date_info = self.env["sale.order.line"].get_available_date(
            product_id,
            values["orderpoint_id"].qty_to_order
            if values.get("orderpoint_id", False)
            else 1,
            date_requested,
        )
        if avail_date:
            date_planned = avail_date - relativedelta(days=product_id.produce_delay)
        else:
            date_planned = fields.Datetime.now() + relativedelta(
                days=product_id.produce_delay
            )
        # ignore company_id.manufacturing_lead for date planned
        format_date_planned = fields.Datetime.from_string(values["date_planned"])
        if date_planned == format_date_planned:
            date_planned = date_planned - relativedelta(hours=1)
        return date_planned
