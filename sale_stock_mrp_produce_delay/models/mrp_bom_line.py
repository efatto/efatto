# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.tools.date_utils import relativedelta


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    def get_available_date(self, qty, date_start):
        self.ensure_one()
        delay = 0
        # fixme is this use of qty_available field correct?
        if self.product_id.with_context(to_date=date_start).qty_available < qty:
            if not self.product_id.bom_ids:
                delay = self.product_id.purchase_delay
            else:
                # fixme need to filter boms?
                delay = max(self.product_id.bom_ids[0].mapped(
                    'bom_line_ids.product_id.purchase_delay')
                )
        available_date = date_start + relativedelta(days=int(delay))
        return available_date
