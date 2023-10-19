from odoo import models


class Orderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    def _prepare_procurement_values(self, date=False, group=False):
        res = super(Orderpoint, self)._prepare_procurement_values(date, group)
        # note: use_po_lead should be deactivated, else purchase order date will be in
        # the past
        # (corresponding to use_security_lead for sale)
        # if self:
        #     line = self.env["sale.order.line"]
        #     avail_date, avail_date_info = line.get_available_date(
        #         self.product_id,
        #         1,
        #         date and date.date() or fields.Date.context_today(self),
        #     )
        #     # FIXME set product_qty as 1 because _prepare_procurement_values does not
        #     #  pass product_qty anymore, did it was useful? or passed? from who?
        #     if avail_date:
        #         res["date_planned"] = fields.Datetime.from_string(avail_date).replace(
        #             hour=10
        #         )
        #         # set default to hour 10, as 2 of night seems akward, even if it would
        #         # be ok
        return res
