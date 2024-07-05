from datetime import datetime, time

from odoo import fields, models
from odoo.tools.date_utils import relativedelta


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _product_available(self, field_names=None, arg=False):
        """
        Compatibility method
        Extended with forecast date.
        """
        return self._compute_quantities_dict(
            self._context.get("lot_id"),
            self._context.get("owner_id"),
            self._context.get("package_id"),
            self._context.get("from_date"),
            datetime.combine(
                fields.Date.today()
                + relativedelta(days=self.env.company.forecast_lead),
                time.max,
            )
            # self._context.get('to_date'),
        )
