# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models

from odoo.addons.server_env.models.server import running


class Fetchmail(models.Model):
    _inherit = "fetchmail.server"

    @running
    def fetch_mail(self):
        return super().fetch_mail()

    @running
    def connect(self):
        return super().connect()
