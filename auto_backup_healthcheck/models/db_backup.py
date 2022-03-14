# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models, _
from odoo.tools import config, ustr
from contextlib import contextmanager
import requests


class DbBackup(models.Model):
    _inherit = 'db.backup'

    @api.multi
    @contextmanager
    def backup_log(self):
        res = super().backup_log()
        url = config.get("healthcheck_url")
        if url and res:
            if _("Database backup succeeded.") in self.message_ids[0].body:
                msg = self.message_ids[0].body
                arguments = {'arg0': ustr(msg), "action": "update"}
                r = requests.post(url, data=arguments)
                r.raise_for_status()
