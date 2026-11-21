# Copyright 2026 Sergio Corato
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AiBridgeExecution(models.Model):
    _inherit = "ai.bridge.execution"

    def _process_response_helpdesk_draft(self, response):
        """Receive the draft from the external system (immediate call or webhook)."""
        self.ensure_one()
        if self.sudo().model_id.model != "helpdesk.ticket":
            return {}
        ticket = self.env["helpdesk.ticket"].sudo().browse(self.res_id).exists()
        if ticket:
            ticket._ai_receive_draft(response, execution=self)
        return {}
