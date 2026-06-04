from unittest.mock import patch

from odoo.tests.common import SavepointCase
from odoo.tools.config import config


class TestServerEnvCron(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = cls.env["res.users"].create(
            {
                "login": "user1@somemail.com",
                "email": "user1@somemail.com",
                "partner_id": cls.env["res.partner"].create({"name": "User 1"}).id,
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            cls.env.ref("base.group_user").id,
                            cls.env.ref("base.group_partner_manager").id,
                        ],
                    )
                ],
            }
        )

    def test_01_check_server_env_running(self):
        ir_actions_servers = self.env["ir.actions.server"].search([])
        for ir_actions_server in ir_actions_servers:
            self.assertEqual(
                ir_actions_server.is_server_env_running,
                True,
            )

    def test_02_check_server_env_test(self):
        with patch.dict(config.options, {"running_env": "test"}):
            ir_actions_servers = self.env["ir.actions.server"].search([])
            for ir_actions_server in ir_actions_servers:
                self.assertEqual(
                    ir_actions_server.is_server_env_running,
                    False,
                )

            # Create a test record to modify
            test_partner = self.env["res.partner"].create({"name": "Test Partner"})

            # 1. Server action linked to a cron (usage='ir_cron')
            cron_action = self.env["ir.actions.server"].create(
                {
                    "name": "Test Cron Action",
                    "model_id": self.env.ref("base.model_res_partner").id,
                    "state": "code",
                    "code": "record.write({'comment': 'Executed'})",
                    "usage": "ir_cron",
                }
            )

            # Should be blocked
            res_cron = cron_action.with_context(active_id=test_partner.id).run()
            self.assertFalse(
                res_cron, "Cron action should be blocked in test environment"
            )
            self.assertFalse(
                test_partner.comment,
                "Partner comment should not be updated by cron action",
            )

            # 2. Regular server action (usage='ir_actions_server')
            regular_action = self.env["ir.actions.server"].create(
                {
                    "name": "Test Regular Action",
                    "model_id": self.env.ref("base.model_res_partner").id,
                    "state": "code",
                    "code": "record.write({'comment': 'Executed Regular'})",
                }
            )

            # Should be executed
            regular_action.with_context(active_id=test_partner.id).run()
            self.assertEqual(
                test_partner.comment,
                "Executed Regular",
                "Regular action should be executed even in test environment",
            )
