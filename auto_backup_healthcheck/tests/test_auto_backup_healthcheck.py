# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from unittest.mock import patch

from odoo.tests import new_test_user
from odoo.tools.translate import get_translation

from odoo.addons.auto_backup.tests.test_db_backup import TestDbBackup

MODEL = "odoo.addons.auto_backup_healthcheck.models.db_backup"
PARAM_KEY = "auto_backup_healthcheck.url"


class TestAutoBackupHealthcheck(TestDbBackup):
    def test_action_backup_success_notifies_healthcheck(self):
        """A successful backup by an ``it_IT`` user notifies the health check.

        The success message posted by ``auto_backup`` is translated, so the
        health check must not rely on its body to detect a successful backup.
        """
        self.env["res.lang"]._activate_lang("it_IT")
        user = new_test_user(
            self.env,
            login="backup_it",
            lang="it_IT",
            groups="base.group_erp_manager,base.group_system",
        )
        url = "https://healthcheck.example.com/backup"
        self.env["ir.config_parameter"].sudo().set_param(PARAM_KEY, url)
        rec_id = self.new_record("local")
        with (
            patch("odoo.service.db.dump_db"),
            patch(f"{MODEL}.requests.post") as mock_post,
        ):
            rec_id.with_user(user).action_backup()
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], url)
        self.assertEqual(kwargs["timeout"], 100)
        self.assertEqual(kwargs["data"]["action"], "update")
        # The notified message is the translated (Italian) success message.
        body = get_translation("auto_backup", "it_IT", "Database backup succeeded.", ())
        self.assertIn(body, kwargs["data"]["arg0"])
        mock_post.return_value.raise_for_status.assert_called_once_with()
