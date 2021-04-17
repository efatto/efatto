# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.addons.server_running_env.models.server_running_env import server_running_env


class Fetchmail(models.Model):
    _inherit = 'fetchmail.server'

    @server_running_env
    @api.multi
    def fetch_mail(self):
        return super().fetch_mail()

    @server_running_env
    @api.multi
    def connect(self):
        return super().connect()
