from odoo import _, api, models
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.constrains("date_start")
    def _check_commitment_date(self):
        # check that date_start is greater than commitment_date
        for rec in self:
            if (
                rec.state in ("draft", "confirmed")
                and rec.date_start
                and rec.commitment_date
                and rec.commitment_date < rec.date_start
            ):
                raise UserError(
                    _(
                        "Production start date {date_start} cannot be after "
                        "commitment date {commitment_date}"
                    ).format(
                        date_start=rec.date_start,
                        commitment_date=rec.commitment_date,
                    )
                )
