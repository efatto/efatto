from odoo import _, api, models
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.constrains("date_start")
    def _check_commitment_date(self):
        # check that date_start is greater than commitment_date
        if (
            self.state in ("draft", "confirmed")
            and self.date_start
            and self.commitment_date
            and self.commitment_date < self.date_start
        ):
            raise UserError(
                _(
                    "Production start date {date_start} cannot be after "
                    "commitment date {commitment_date}"
                ).format(
                    date_start=self.date_start,
                    commitment_date=self.commitment_date,
                )
            )
