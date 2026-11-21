# Copyright 2026 Sergio Corato
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AiBridgeExecution(models.Model):
    _inherit = "ai.bridge.execution"

    def _add_extra_payload_fields(self, payload):
        """The envelope of the bridge names the customer database.

        ``ai_oca_bridge`` adds ``_odoo = {db, db_name, db_hash, user_id}`` and,
        for asynchronous bridges, ``_response_url`` built on the base URL:
        ``db_name`` is usually ``<customer>_prod`` and the base URL is the
        customer's domain, so they would defeat the pseudonymization of the
        question. The database uuid and hash stay, they identify the instance
        without naming it.
        """
        payload = super()._add_extra_payload_fields(payload)
        if self.ai_bridge_id.payload_type == "helpdesk_question" and isinstance(
            payload, dict
        ):
            odoo_info = payload.get("_odoo")
            if isinstance(odoo_info, dict):
                odoo_info.pop("db_name", None)
                odoo_info.pop("user_id", None)
        return payload

    def _process_response_helpdesk_draft(self, response):
        """Receive the draft from the external system (immediate call or webhook)."""
        self.ensure_one()
        if self.sudo().model_id.model != "helpdesk.ticket":
            return {}
        ticket = self.env["helpdesk.ticket"].sudo().browse(self.res_id).exists()
        if ticket:
            ticket._ai_receive_draft(response, execution=self)
        return {}
