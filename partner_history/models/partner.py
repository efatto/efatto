# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    res_partner_history_ids = fields.One2many(
        comodel_name="res.partner.history",
        inverse_name="partner_id",
        string="Partner history",
    )
