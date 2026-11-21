# Copyright 2026 Sergio Corato
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import json

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from ..tools.pseudonymizer import Pseudonymizer

PARAM_PREFIX = "helpdesk_mgmt_ai."


class HelpdeskAiQa(models.Model):
    """Archive of validated questions and answers.

    Validated entries are the material the external AI system uses:
    - 'Knowledge base' entries are indexed as sources the model can cite;
    - 'Test set' entries are kept out of the knowledge base and used only to
      measure precision, otherwise the test would reward memorization.
    Texts are pseudonymized and no placeholder table is kept here.
    """

    _name = "helpdesk.ai.qa"
    _description = "Helpdesk AI Question and Answer"
    _order = "create_date desc, id desc"

    name = fields.Char(string="Title", compute="_compute_name", store=True)
    question = fields.Text(required=True)
    answer = fields.Text(required=True)
    source = fields.Selection(
        [
            ("review", "AI draft review"),
            ("import", "Solved ticket import"),
            ("manual", "Manual"),
        ],
        required=True,
        default="manual",
    )
    ticket_id = fields.Many2one(
        "helpdesk.ticket", string="Ticket", ondelete="set null", index=True
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )
    team_id = fields.Many2one("helpdesk.ticket.team", string="Team")
    category_id = fields.Many2one("helpdesk.ticket.category", string="Category")
    state = fields.Selection(
        [
            ("to_validate", "To validate"),
            ("validated", "Validated"),
            ("rejected", "Rejected"),
        ],
        string="Status",
        required=True,
        default="to_validate",
        index=True,
    )
    usage = fields.Selection(
        [("knowledge", "Knowledge base"), ("test", "Test set")],
        required=True,
        default="knowledge",
        help="Test set entries are never given to the model as sources.",
    )
    odoo_version = fields.Char(default="18.0")
    validated_by_id = fields.Many2one("res.users", string="Validated by", readonly=True)
    validation_date = fields.Datetime(readonly=True)
    residue = fields.Text(
        string="Possible Personal Data",
        readonly=True,
        compute="_compute_residue",
        store=True,
        groups="helpdesk_mgmt_ai.group_ai_draft_user",
    )
    has_residue = fields.Boolean(
        string="Possible Personal Data Found",
        compute="_compute_has_residue",
        store=True,
    )
    note = fields.Text()

    @api.depends("question")
    def _compute_name(self):
        for record in self:
            first_line = (record.question or "").strip().splitlines()
            title = first_line[0] if first_line else ""
            record.name = title[:80] + ("..." if len(title) > 80 else "")

    @api.depends("question", "answer", "ticket_id")
    def _compute_residue(self):
        """Stored, so the warning exists before the (blocking) action runs."""
        for record in self:
            text = f"{record.question or ''}\n{record.answer or ''}"
            if not text.strip():
                record.residue = False
                continue
            known = []
            if record.ticket_id:
                known = record.ticket_id.sudo()._ai_known_values(text)
            pseudonymizer = Pseudonymizer()
            residue = pseudonymizer.residue(
                record.question or "", known, strict=True
            ) + pseudonymizer.residue(record.answer or "", known, strict=True)
            record.residue = (
                "\n".join(f"{label}: {value}" for label, value in residue) or False
            )

    @api.depends("residue")
    def _compute_has_residue(self):
        for record in self:
            record.has_residue = bool(record.residue)

    # --- helpers -----------------------------------------------------------------

    @api.model
    def _ai_param(self, key, default=False):
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(PARAM_PREFIX + key, default)
        )

    @api.model
    def _pick_usage(self, ticket_id, test_share):
        """Deterministic split between knowledge base and test set."""
        if not ticket_id or test_share <= 0:
            return "knowledge"
        return "test" if (ticket_id * 2654435761) % 100 < test_share else "knowledge"

    @api.model
    def _default_test_share(self):
        try:
            return int(self._ai_param("test_share_percent", "20") or 0)
        except ValueError:
            return 20

    def _check_residue(self):
        """Recompute the stored residue fields.

        Kept as an explicit entry point for the *Check personal data* button:
        the fields are computed, so a blocked validation does not need to
        write anything (a UserError rolls the request back).
        """
        self.env.add_to_compute(self._fields["residue"], self)
        self.env.add_to_compute(self._fields["has_residue"], self)
        self.flush_recordset(["residue", "has_residue"])
        return True

    def write(self, values):
        """Editing a validated entry sends it back to validation."""
        if {"question", "answer", "usage"} & set(values):
            reset = self.filtered(lambda record: record.state != "to_validate")
            if reset:
                values = dict(
                    values,
                    state="to_validate",
                    validated_by_id=False,
                    validation_date=False,
                )
        return super().write(values)

    # --- actions -------------------------------------------------------------------

    def action_check_residue(self):
        self._check_residue()
        return True

    def action_validate(self):
        self._check_residue()
        blocked = self.filtered("has_residue")
        if blocked:
            raise UserError(
                _(
                    "These entries may still contain personal data. Correct them "
                    "before validating:\n%(names)s\n\n%(values)s",
                    names="\n".join(blocked.mapped("name")),
                    values="\n".join(blocked.mapped("residue")),
                )
            )
        self.write(
            {
                "state": "validated",
                "validated_by_id": self.env.user.id,
                "validation_date": fields.Datetime.now(),
            }
        )
        return True

    def action_reject(self):
        self.write({"state": "rejected"})
        return True

    def action_reset(self):
        self.write(
            {"state": "to_validate", "validated_by_id": False, "validation_date": False}
        )
        return True

    def _export_values(self):
        self.ensure_one()
        return {
            "id": f"QA-{self.id}",
            "question": self.question,
            "answer": self.answer,
            "usage": self.usage,
            "odoo_version": self.odoo_version or "",
            "team": self.team_id.name or "",
            "category": self.category_id.name or "",
            "source": self.source,
            "validated_on": fields.Date.to_string(self.validation_date.date())
            if self.validation_date
            else "",
        }

    def action_export_jsonl(self, usage="knowledge"):
        """Download validated entries as JSON Lines, ready for the RAG index.

        The residue is recomputed first: the stored value cannot see a contact
        created after the entry.
        """
        self._check_residue()
        records = self.filtered(lambda r: r.state == "validated" and r.usage == usage)
        if not records:
            raise UserError(
                _("Select at least one validated entry of usage '%s'.", usage)
            )
        residue = records.filtered("has_residue")
        if residue:
            raise UserError(
                _(
                    "These entries may still contain personal data and cannot be "
                    "exported:\n%s",
                    "\n".join(residue.mapped("name")),
                )
            )
        content = "\n".join(
            json.dumps(record._export_values(), ensure_ascii=False)
            for record in records
        )
        attachment = self.env["ir.attachment"].create(
            {
                "name": f"helpdesk_ai_qa_{usage}_"
                f"{fields.Date.context_today(self)}.jsonl",
                "datas": base64.b64encode(content.encode("utf-8")),
                "mimetype": "application/jsonl",
                "res_model": self._name,
                "res_id": records[0].id,
            }
        )
        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/{attachment.id}?download=true",
            "target": "self",
        }

    @api.model
    def _create_from_review(self, ticket, answer_clean):
        """Entry created when a technician sends an AI draft to the customer."""
        auto_validate = self._ai_param("auto_validate_reviewed", "False") in (
            "1",
            "True",
            "true",
        )
        values = {
            "question": ticket.ai_question_clean,
            "answer": answer_clean,
            "source": "review",
            "ticket_id": ticket.id,
            "company_id": ticket.company_id.id,
            "team_id": ticket.team_id.id,
            "category_id": ticket.category_id.id,
            "usage": self._pick_usage(ticket.id, self._default_test_share()),
        }
        record = self.create(values)
        record._check_residue()
        if auto_validate and not record.has_residue:
            record.write(
                {
                    "state": "validated",
                    "validated_by_id": self.env.user.id,
                    "validation_date": fields.Datetime.now(),
                }
            )
        return record
