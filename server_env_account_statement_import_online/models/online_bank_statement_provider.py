from odoo import api, models

from odoo.addons.server_env.models.server import running


class OnlineBankStatementProvider(models.Model):
    _inherit = "online.bank.statement.provider"

    @running
    @api.model
    def _scheduled_pull(self):
        return super()._scheduled_pull()
