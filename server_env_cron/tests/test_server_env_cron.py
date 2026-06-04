from unittest.mock import patch
from odoo.tools.config import config
from odoo.tests.common import SavepointCase


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
        with patch.dict(config.options, {'running_env': 'test'}):
            ir_actions_servers = self.env["ir.actions.server"].search([])
            for ir_actions_server in ir_actions_servers:
                self.assertEqual(
                    ir_actions_server.is_server_env_running,
                    False,
                )
