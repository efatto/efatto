# Copyright 2026 Sergio Corato
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import html2plaintext

from ..models.helpdesk_ai_draft_log import CONFIDENCE_LEVELS, REVIEW_OUTCOMES
from ..tools.pseudonymizer import Pseudonymizer


def _normalized_text(html):
    return " ".join(html2plaintext(html or "").split())


class HelpdeskAiReviewWizard(models.TransientModel):
    _name = "helpdesk.ai.review.wizard"
    _description = "Review AI Draft"

    ticket_id = fields.Many2one(
        "helpdesk.ticket", string="Ticket", required=True, readonly=True
    )
    outcome = fields.Selection(
        REVIEW_OUTCOMES, string="Outcome", required=True, default="approved"
    )
    answer = fields.Html(string="Reply to the Customer", sanitize=True)
    reason_id = fields.Many2one(
        "helpdesk.ai.review.reason",
        string="Reason",
        help="Required when the draft is modified or rejected.",
    )
    reason_requires_note = fields.Boolean(
        related="reason_id.requires_note", string="Note Required"
    )
    note = fields.Text(string="Note")
    send_to_customer = fields.Boolean(
        string="Send the Reply to the Customer", default=True
    )
    confidence = fields.Selection(
        CONFIDENCE_LEVELS, related="ticket_id.ai_confidence", string="Confidence"
    )
    confidence_reason = fields.Char(
        related="ticket_id.ai_confidence_reason", string="Confidence Reason"
    )
    abstained = fields.Boolean(
        related="ticket_id.ai_abstained", string="The Model Abstained"
    )
    sources = fields.Html(related="ticket_id.ai_sources", string="Cited Sources")

    @api.model
    def default_get(self, fields_list):
        values = super().default_get(fields_list)
        ticket = self.env["helpdesk.ticket"].browse(
            values.get("ticket_id") or self.env.context.get("default_ticket_id")
        )
        if ticket and "answer" in fields_list:
            values["answer"] = ticket.ai_draft
        if ticket.ai_abstained and "outcome" in fields_list:
            values["outcome"] = "rejected"
            values["send_to_customer"] = False
        return values

    @api.onchange("outcome")
    def _onchange_outcome(self):
        if self.outcome == "rejected":
            self.send_to_customer = False
        if self.outcome == "approved":
            self.answer = self.ticket_id.ai_draft

    def _effective_outcome(self):
        """A draft marked as approved but with a changed text counts as modified."""
        self.ensure_one()
        if self.outcome == "approved" and _normalized_text(self.answer) != _normalized_text(
            self.ticket_id.ai_draft
        ):
            return "modified"
        return self.outcome

    def action_confirm(self):
        self.ensure_one()
        ticket = self.ticket_id
        ticket._ai_check_user()
        if ticket.ai_state != "draft_ready":
            raise UserError(_("This draft has already been reviewed."))
        outcome = self._effective_outcome()
        if outcome != "approved" and not self.reason_id:
            if outcome == "modified":
                raise UserError(_("Select a reason: the draft has been modified."))
            raise UserError(_("Select a reason: the draft has been rejected."))
        if self.reason_id.requires_note and not (self.note or "").strip():
            raise UserError(_("The reason '%s' requires a note.", self.reason_id.name))
        send = self.send_to_customer and outcome != "rejected"
        if send:
            if not _normalized_text(self.answer):
                raise UserError(_("The reply to the customer is empty."))
            ticket.message_post(
                body=self.answer,
                message_type="comment",
                subtype_xmlid="mail.mt_comment",
                partner_ids=ticket.partner_id.ids,
            )
        final_clean = False
        if outcome != "rejected":
            pseudonymizer = Pseudonymizer(ticket.ai_placeholder_map or {})
            final_clean, _pseudonymizer, _known = ticket._ai_pseudonymize(
                html2plaintext(self.answer or ""), pseudonymizer
            )
        self.env["helpdesk.ai.draft.log"].create(
            {
                "ticket_id": ticket.id,
                "execution_id": ticket.ai_execution_id.id,
                "model_name": ticket.ai_model_name,
                "question_clean": ticket.ai_question_clean,
                "draft_clean": ticket.ai_draft_clean,
                "final_answer_clean": final_clean,
                "abstained": ticket.ai_abstained,
                "confidence_declared": ticket.ai_confidence_declared,
                "confidence": ticket.ai_confidence,
                "confidence_reason": ticket.ai_confidence_reason,
                "outcome": outcome,
                "reason_id": self.reason_id.id if outcome != "approved" else False,
                "note": self.note,
                "sent_to_customer": send,
            }
        )
        if send and final_clean:
            # The reply checked by the technician extends the archive
            self.env["helpdesk.ai.qa"].sudo()._create_from_review(ticket, final_clean)
        ticket.ai_state = "done"
        return {"type": "ir.actions.act_window_close"}
