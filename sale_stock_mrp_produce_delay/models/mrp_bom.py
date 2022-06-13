# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    def get_bom_available_date(self, qty, date_start):
        self.ensure_one()
        bom_available_date = max(
            [line.get_available_date(qty, date_start) for line in self.bom_line_ids]
        )
        return bom_available_date

    # todo time to produce this bom and childrens
