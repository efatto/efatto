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
            model = action.model_id.exists()
            if model and model.model and not action.model_name:
                # model_name is a stored related field: after direct SQL
                # inserts/migrations it can be out of sync with model_id.
                # Recompute it before base run() uses it for access checks.
                action.modified(["model_id"])
                action.recompute(["model_name"])
            if not model or not model.model or not action.model_name:
                # A server action without a valid model cannot be run: base
                # run() would fail with KeyError(model_name) on access checks.
                _logger.warning(
                    "Execution of server action '%s' skipped as no valid model "
                    "is configured (model_id: %s, model_name: %s). "
                    "(Action ID: %s)",
                    action.name,
                    action.model_id.id or False,
                    action.model_name,
                    action.id,
                )
                continue
            if (
                not action.is_production_server
                and model.model != "openupgrader.migration"
                and (action.usage == "ir_cron" or action.env.context.get("lastcall"))
            ):
                # Log the block for traceability.
                _logger.info(
                    "Execution of cron '%s' blocked as server state is not running "
                    "and it is not a migration action (model: %s). "
                    "(Action ID: %s)",
                    action.name,
                    model.model,
                    action.id,
                )
            else:
                action_todo |= action

        if not action_todo:
            return False
        return super(IrActionsServer, action_todo).run()
