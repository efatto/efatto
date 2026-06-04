import logging

from odoo import models

_logger = logging.getLogger(__name__)


class IrActionsServer(models.Model):
    _inherit = ["ir.actions.server", "server.env.running"]
    _name = "ir.actions.server"

    def run(self):
        # 1. Check if the server state is allowed to run crons.
        # 2. Verify if the action is actually used by a cron.
        # Server actions linked to crons usually have usage='ir_cron'
        # or are called within an ir.cron execution context (lastcall in context).
        for action in self:
            if not action.is_server_env_running and (
                action.usage == "ir_cron" or action.env.context.get("lastcall")
            ):
                # Log the block for traceability.
                _logger.info(
                    "Execution of cron '%s' blocked as server state is not running. "
                    "(Action ID: %s)",
                    action.name,
                    action.id,
                )
                return False

        return super().run()
