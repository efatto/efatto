# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.addons.server_running_env.models.server_running_env import server_running_env


class MailMail(models.Model):
    _inherit = 'mail.mail'

    @server_running_env
    @api.multi
    def send(self, auto_commit=False, raise_exception=False):
        return super().send(auto_commit=auto_commit, raise_exception=raise_exception)
