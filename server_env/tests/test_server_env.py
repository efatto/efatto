from unittest.mock import patch

from odoo.tests import new_test_user
from odoo.tools.config import config

from odoo.addons.base.tests.common import BaseCommon


class TestServerEnv(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = new_test_user(
            cls.env,
            login="user1@somemail.com",
            email="user1@somemail.com",
            partner_id=cls.env["res.partner"].create({"name": "User 1"}).id,
            groups="base.group_user,base.group_partner_manager",
        )

    def test_01_check_server_env_running(self):
        with patch.dict(config.options, {"running_env": "prod"}):
            ir_actions_servers = self.env["ir.actions.server"].search([])
            for ir_actions_server in ir_actions_servers:
                self.assertEqual(
                    ir_actions_server.is_production_server,
                    True,
                )
            # Create a test record to modify
            test_partner = self.env["res.partner"].create({"name": "Test Partner"})
            self.assertTrue(test_partner)

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

            # Should be executed
            cron_action.with_context(
                active_id=test_partner.id,
                active_ids=test_partner.ids,
                active_model="res.partner",
            ).run()
            self.assertTrue(
                "Executed" in test_partner.comment,
                "Partner comment should be updated by cron action in prod environment",
            )

            # 2. Regular server action (usage='ir_actions_server')
            regular_action = self.env["ir.actions.server"].create(
                {
                    "name": "Test Regular Action",
                    "model_id": self.env.ref("base.model_res_partner").id,
                    "state": "code",
                    "code": "record.write({'comment': 'Second Execution'})",
                }
            )
            # Should be executed
            regular_action.with_context(
                active_id=test_partner.id,
                active_ids=test_partner.ids,
                active_model="res.partner",
            ).run()
            self.assertTrue(
                "Second Execution" in test_partner.comment,
                "Regular action should be executed even in test environment",
            )

    def test_02_check_server_env_test(self):
        with patch.dict(config.options, {"running_env": "test"}):
            ir_actions_servers = self.env["ir.actions.server"].search([])
            for ir_actions_server in ir_actions_servers:
                self.assertEqual(
                    ir_actions_server.is_production_server,
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
            cron_action.with_context(
                active_id=test_partner.id,
                active_ids=test_partner.ids,
                active_model="res.partner",
            ).run()
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
            regular_action.with_context(
                active_id=test_partner.id,
                active_ids=test_partner.ids,
                active_model="res.partner",
            ).run()
            self.assertTrue(
                "Executed Regular" in test_partner.comment,
                "Regular action should be executed even in test environment",
            )
