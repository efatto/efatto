import logging

from odoo import models

_logger = logging.getLogger(__name__)


class IrActionsServer(models.Model):
    _inherit = ["ir.actions.server", "server.env.state"]
    _name = "ir.actions.server"

    def run(self):
        # 1. Check if the server state is allowed to run crons.
        # 2. Verify if the action is actually used by a cron.
        # Server actions linked to crons usually have usage='ir_cron'
        # or are called within an ir.cron execution context (lastcall in context).
        action_todo = self.env["ir.actions.server"]
        for action in self.sudo():
            if (
                not action.is_production_server
                and not action.model_id.model == "openupgrader.migration"
                and (action.usage == "ir_cron" or action.env.context.get("lastcall"))
            ):
                # Log the block for traceability.
                _logger.info(
                    "Execution of cron '%s' blocked as server state is not running "
                    "and it is not a migration action (model: %s). "
                    "(Action ID: %s)",
                    action.name,
                    action.model_id.model,
                    action.id,
                )
            else:
                action_todo |= action

        return super(IrActionsServer, action_todo).run()
