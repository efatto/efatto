# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models, fields


class WizardGiornale(models.TransientModel):
    _inherit = "wizard.giornale"

    print_row = fields.Integer('Row for page', required=True, default=38)

    def _prepare_datas_form(self):
        wizard = self
        datas_form = super()._prepare_datas_form()
        datas_form['print_row'] = wizard.print_row
        return datas_form
