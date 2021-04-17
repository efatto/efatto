# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.addons.server_running_env.models.server_running_env import server_running_env


class GoogleCalendar(models.AbstractModel):
    _inherit = "google.calendar"

    @server_running_env
    def get_token(self):
        return super().get_token()
