# Copyright 2026 Sergio Corato
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import UserError


class AiBridge(models.Model):
    _inherit = "ai.bridge"

    payload_type = fields.Selection(
        selection_add=[("helpdesk_question", "Helpdesk: pseudonymized question")],
        ondelete={"helpdesk_question": lambda recs: recs.write({"payload_type": "none"})},
    )
    result_type = fields.Selection(
        selection_add=[("helpdesk_draft", "Helpdesk: draft reply")],
        ondelete={"helpdesk_draft": lambda recs: recs.write({"result_type": "none"})},
    )

    def _prepare_payload_helpdesk_question(self, record=None, **kwargs):
        """Send only the pseudonymized question and the technical context.

        No field of the ticket or of the customer is read directly: the text
        sent is the one approved by the technician.
        """
        if not record or record._name != "helpdesk.ticket":
            raise UserError(
                _("The bridge '%s' can only be used with helpdesk tickets.", self.display_name)
            )
        return record._ai_prepare_bridge_payload()
