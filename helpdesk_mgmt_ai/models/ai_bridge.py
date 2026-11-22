# Copyright 2026 Sergio Corato
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class AiBridge(models.Model):
    _inherit = "ai.bridge"

    payload_type = fields.Selection(
        selection_add=[("helpdesk_question", "Helpdesk: pseudonymized question")],
        ondelete={
            "helpdesk_question": lambda recs: recs.write({"payload_type": "none"})
        },
    )
    result_type = fields.Selection(
        selection_add=[("helpdesk_draft", "Helpdesk: draft reply")],
        ondelete={"helpdesk_draft": lambda recs: recs.write({"result_type": "none"})},
    )

    @api.constrains("usage", "payload_type")
    def _check_helpdesk_question_usage(self):
        """An automatic bridge would send the question on every ticket write."""
        for bridge in self:
            if bridge.payload_type == "helpdesk_question" and bridge.usage != "none":
                raise ValidationError(
                    _(
                        "The payload type 'Helpdesk: pseudonymized question' can "
                        "only be used with usage 'None': the question is sent by "
                        "the ticket buttons, never automatically."
                    )
                )

    def _sample_payload_helpdesk_question(self):
        """Example shown on the bridge form (the payload is computed on read)."""
        return {
            "question": "[PERSON_1] cannot send invoice [DOCUMENT_1]: "
            "the SdI rejects it with error 00305.",
            "ticket": "TICKET-0",
            "language": "it_IT",
            "odoo": {"version": "18.0", "edition": "community"},
            "installed_modules": ["account", "l10n_it"],
            "abstention_text": "I have no verified information to answer.",
            "confidence_levels": ["high", "medium", "low"],
        }

    def _prepare_payload_helpdesk_question(self, record=None, **kwargs):
        """Send only the pseudonymized question and the technical context.

        No field of the ticket or of the customer is read directly: the text
        sent is the one approved by the technician. The gate is repeated in
        the ticket model, because this method is also reachable from
        ``execute_ai_bridge``.
        """
        if not record and self.env.context.get("sample_payload"):
            # ai_oca_bridge computes `sample_payload` with no record while
            # rendering the bridge form: raising here makes the form unreadable.
            return self._sample_payload_helpdesk_question()
        if not record or record._name != "helpdesk.ticket":
            raise UserError(
                _(
                    "The bridge '%s' can only be used with helpdesk tickets.",
                    self.display_name,
                )
            )
        return record._ai_prepare_bridge_payload()
