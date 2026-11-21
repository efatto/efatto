# Copyright 2026 Sergio Corato
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models

CONFIDENCE_LEVELS = [
    ("high", "High"),
    ("medium", "Medium"),
    ("low", "Low"),
]

REVIEW_OUTCOMES = [
    ("approved", "Approved as is"),
    ("modified", "Modified"),
    ("rejected", "Rejected"),
]


class HelpdeskAiDraftLog(models.Model):
    """Log of the drafts: feeds the test set and the metrics.

    The question and the draft are pseudonymized, but this is not an
    anonymous dataset: ``note`` and ``confidence_reason`` are free text and
    may quote the value that slipped through (the review reason 'Personal data
    slipped through' forces a note). Do not export this model as a training
    set: it is an operational log.
    """

    _name = "helpdesk.ai.draft.log"
    _description = "Helpdesk AI Draft Log"
    _order = "create_date desc, id desc"
    _rec_name = "ticket_id"

    ticket_id = fields.Many2one(
        "helpdesk.ticket",
        string="Ticket",
        required=True,
        ondelete="cascade",
        index=True,
    )
    company_id = fields.Many2one(
        related="ticket_id.company_id", string="Company", store=True, index=True
    )
    team_id = fields.Many2one(related="ticket_id.team_id", string="Team", store=True)
    category_id = fields.Many2one(
        related="ticket_id.category_id", string="Category", store=True
    )
    user_id = fields.Many2one(
        "res.users", string="Technician", default=lambda self: self.env.user
    )
    execution_id = fields.Many2one(
        "ai.bridge.execution", string="Bridge Execution", ondelete="set null"
    )
    model_name = fields.Char(string="Model")
    question_clean = fields.Text(string="Question Sent")
    draft_clean = fields.Text(string="Model Draft")
    final_answer_clean = fields.Text(string="Final Reply (pseudonymized)")
    abstained = fields.Boolean(string="Abstention")
    confidence_declared = fields.Selection(
        CONFIDENCE_LEVELS, string="Declared Confidence"
    )
    confidence = fields.Selection(CONFIDENCE_LEVELS, string="Final Confidence")
    confidence_reason = fields.Char()
    outcome = fields.Selection(REVIEW_OUTCOMES, required=True)
    reason_id = fields.Many2one(
        "helpdesk.ai.review.reason", string="Reason", ondelete="restrict"
    )
    note = fields.Text()
    sent_to_customer = fields.Boolean(string="Sent to Customer")
