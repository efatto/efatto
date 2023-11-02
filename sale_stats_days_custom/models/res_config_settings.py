# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    sale_stat_days = fields.Integer(
        string="Days for sale statistics",
        default=365,
        help="Number of days for sale statistic shown in smart buttons in product.",
    )


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sale_stat_days = fields.Integer(
        related="company_id.sale_stat_days",
        string="Days for sale statistics",
        help="Number of days for sale statistic shown in smart buttons in product.",
        readonly=False,
    )
