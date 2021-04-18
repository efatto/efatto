# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.addons.server_env.models.server import running


class Fetchmail(models.Model):
    _inherit = 'fetchmail.server'

    @running
    @api.multi
    def fetch_mail(self):
        return super().fetch_mail()

    @running
    @api.multi
    def connect(self):
        return super().connect()
