# Copyright 2015 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2024 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    check_chronology = fields.Boolean()

    @api.onchange("type")
    def _onchange_type_for_alias(self):
        res = super()._onchange_type_for_alias()
        if self.type not in ["sale", "purchase"]:
            self.check_chronology = False
        return res
