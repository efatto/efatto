from odoo import _, api, models
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.constrains("date_planned_start")
    def _check_commitment_date(self):
        # check that date_planned_start is greater than commitment_date
        if (
            self.state in ("draft", "confirmed")
            and self.date_planned_start
            and self.commitment_date
            and self.commitment_date < self.date_planned_start
        ):
            raise UserError(
                _(
                    "Production start date {date_planned_start} cannot be after "
                    "commitment date {commitment_date}"
                ).format(
                    date_planned_start=self.date_planned_start,
                    commitment_date=self.commitment_date,
                )
            )
