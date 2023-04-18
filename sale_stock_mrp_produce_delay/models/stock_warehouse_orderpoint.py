from odoo import fields, models


class Orderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    def _prepare_procurement_values(
        self, product_qty, date=False, group=False
    ):
        res = super(Orderpoint, self)._prepare_procurement_values(
            product_qty, date, group
        )
        # note: use_po_lead should be deactivated, else purchase order date will be in
        # the past
        # (corresponding to use_security_lead for sale)
        if self:
            line = self.env['sale.order.line']
            avail_date, avail_date_info = line.get_available_date(
                self.product_id,
                product_qty,
                date or fields.Date.context_today(self))
            res["date_planned"] = fields.Datetime.from_string(
                avail_date).replace(hour=10)
            # set default to hour 10, as 2 of night seems akward, even if it would be ok
        return res
