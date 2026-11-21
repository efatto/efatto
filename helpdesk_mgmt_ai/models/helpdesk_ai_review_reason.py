# Copyright 2026 Sergio Corato
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HelpdeskAiReviewReason(models.Model):
    _name = "helpdesk.ai.review.reason"
    _description = "AI Draft Review Reason"
    _order = "sequence, id"

    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    requires_note = fields.Boolean(
        string="Note Required",
        help="The technician must explain the reason with a note.",
    )
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ("code_unique", "unique(code)", "The reason code must be unique."),
    ]
