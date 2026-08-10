# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import functools
import logging

from odoo import fields, models
from odoo.tools.config import config as system_base_config

logger = logging.getLogger(__name__)


def running(func):
    @functools.wraps(func)
    def wrap(*args, **kwargs):
        if not system_base_config.get("running_env"):
            system_base_config["running_env"] = "test"
        server_running_state = system_base_config.get("running_env")
        if server_running_state == "prod":
            result = func(*args, **kwargs)
        else:
            logger.info(
                "Server state != prod, ignored %s function" % func.__name__
            )
            result = False
        return result

    return wrap


class ServerEnvState(models.AbstractModel):
    _name = "server.env.state"
    _description = "Server Env State"

    server_env_state = fields.Selection(
        [
            ("prod", "prod"),
            ("migr", "migr"),
            ("test", "test"),
        ],
        compute="_compute_server_env_state",
    )
    is_production_server = fields.Boolean(
        compute="_compute_server_env_state",
    )

    def _compute_server_env_state(self):
        for record in self:
            server_env_state = system_base_config.get("running_env", "prod")
            record.server_env_state = server_env_state
            record.is_production_server = bool(server_env_state == "prod")
