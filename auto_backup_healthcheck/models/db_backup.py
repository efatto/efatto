# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import requests

from odoo import models


class DbBackup(models.Model):
    _inherit = "db.backup"

    def action_backup(self):
        res = super().action_backup()
        url = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("auto_backup_healthcheck.url", False)
        )
        if url:
            failure_subtype = self.env.ref("auto_backup.mail_message_subtype_failure")
            for backup in self:
                # The last message is the one posted by ``backup_log``: it is a
                # failure only when it uses the failure subtype.
                last_message = backup.message_ids[:1]
                if last_message and last_message.subtype_id != failure_subtype:
                    arguments = {"arg0": last_message.body, "action": "update"}
                    requests.post(url, data=arguments, timeout=100).raise_for_status()
        return res
