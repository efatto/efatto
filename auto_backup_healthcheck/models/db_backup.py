# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models, _
from odoo.tools import ustr

import requests


class DbBackup(models.Model):
    _inherit = 'db.backup'

    @api.multi
    def action_backup(self):
        super().action_backup()
        url = self.env['ir.config_parameter'].sudo().get_param(
            "healthcheck_url", False)
        if url:
            for backup in self:
                if _("Database backup succeeded.") in backup.message_ids[0].body:
                    msg = backup.message_ids[0].body
                    arguments = {'arg0': ustr(msg), "action": "update"}
                    r = requests.post(url, data=arguments)
                    r.raise_for_status()
