# Copyright 2026 Sergio Corato
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import html2plaintext

from ..tools.pseudonymizer import Pseudonymizer


class HelpdeskAiQaImportWizard(models.TransientModel):
    """Retrieve solved tickets to extend the question and answer archive.

    For each solved ticket, the question is the subject and description, the
    answer is the reply (or replies) sent by the support staff. Both are
    pseudonymized and created as entries to validate: old answers may be
    wrong or refer to another version.
    """

    _name = "helpdesk.ai.qa.import.wizard"
    _description = "Import Solved Tickets into the AI Archive"

    date_from = fields.Date(string="Closed from")
    date_to = fields.Date(string="Closed to")
    team_ids = fields.Many2many("helpdesk.ticket.team", string="Teams")
    category_ids = fields.Many2many("helpdesk.ticket.category", string="Categories")
    answer_mode = fields.Selection(
        [("last", "Last staff reply"), ("all", "All staff replies")],
        string="Answer",
        required=True,
        default="last",
    )
    test_share = fields.Integer(
        string="Share for the Test Set (%)",
        default=lambda self: self.env["helpdesk.ai.qa"]._default_test_share(),
        help="Part of the entries kept out of the knowledge base and used only "
        "to measure precision.",
    )
    limit = fields.Integer(string="Maximum Tickets", default=200)
    ticket_count = fields.Integer(
        string="Tickets Found", compute="_compute_ticket_count"
    )

    @api.constrains("test_share")
    def _check_test_share(self):
        for wizard in self:
            if not 0 <= wizard.test_share <= 100:
                raise UserError(
                    _("The share for the test set must be between 0 and 100.")
                )

    @api.constrains("limit")
    def _check_limit(self):
        for wizard in self:
            # search(limit=-1) means "no limit": a first run would import the
            # whole history.
            if wizard.limit < 1:
                raise UserError(_("The maximum number of tickets must be positive."))

    def _closed_date_field(self):
        ticket_fields = self.env["helpdesk.ticket"]._fields
        return "closed_date" if "closed_date" in ticket_fields else "write_date"

    def _ticket_domain(self):
        self.ensure_one()
        domain = []
        if "closed" in self.env["helpdesk.ticket.stage"]._fields:
            domain.append(("stage_id.closed", "=", True))
        else:
            domain.append((self._closed_date_field(), "!=", False))
        date_field = self._closed_date_field()
        if self.date_from:
            domain.append((date_field, ">=", self.date_from))
        if self.date_to:
            domain.append((date_field, "<", fields.Date.add(self.date_to, days=1)))
        if self.team_ids:
            domain.append(("team_id", "in", self.team_ids.ids))
        if self.category_ids:
            domain.append(("category_id", "in", self.category_ids.ids))
        if "company_id" in self.env["helpdesk.ticket"]._fields:
            domain.append(("company_id", "in", self.env.companies.ids))
        archived = self.env["helpdesk.ai.qa"].search([("ticket_id", "!=", False)])
        if archived:
            domain.append(("id", "not in", archived.mapped("ticket_id").ids))
        return domain

    @api.depends("date_from", "date_to", "team_ids", "category_ids")
    def _compute_ticket_count(self):
        # The archive manager sees all solved tickets of the allowed companies
        Ticket = self.env["helpdesk.ticket"].sudo()
        for wizard in self:
            wizard.ticket_count = Ticket.search_count(wizard._ticket_domain())

    def _is_staff_author(self, ticket, message):
        """True for an internal user or for an automation posting as OdooBot."""
        author = message.author_id
        if not author:
            return True
        if author == self.env.ref("base.partner_root", raise_if_not_found=False):
            # Automation, cron or a sudo() post: still a staff reply
            return True
        if ticket.partner_id and author == ticket.partner_id:
            return False
        users = author.user_ids
        if not users:
            # An unknown contact, e.g. a third party replying by e-mail
            return False
        return any(not user.share for user in users)

    def _staff_replies(self, ticket):
        """Replies sent to the customer by the staff, oldest first."""
        comment = self.env.ref("mail.mt_comment")
        messages = ticket.message_ids.filtered(
            lambda m: m.message_type in ("comment", "email")
            and m.subtype_id == comment
            and self._is_staff_author(ticket, m)
            and html2plaintext(m.body or "").strip()
        )
        return messages.sorted(lambda m: (m.date, m.id))

    def _answer_text(self, ticket):
        replies = self._staff_replies(ticket)
        if not replies:
            return ""
        if self.answer_mode == "last":
            replies = replies[-1:]
        return "\n\n".join(html2plaintext(m.body).strip() for m in replies)

    def action_import(self):
        self.ensure_one()
        Qa = self.env["helpdesk.ai.qa"]
        date_field = self._closed_date_field()
        tickets = (
            self.env["helpdesk.ticket"]
            .sudo()
            .search(
                self._ticket_domain(),
                limit=self.limit or None,
                order=f"{date_field} desc",
            )
        )
        if not tickets:
            raise UserError(_("No solved ticket matches the filters."))
        created = Qa.browse()
        skipped = 0
        for ticket in tickets:
            answer = self._answer_text(ticket)
            if not answer:
                skipped += 1
                continue
            pseudonymizer = Pseudonymizer()
            question_clean, pseudonymizer, _known = ticket._ai_pseudonymize(
                ticket._ai_source_text(), pseudonymizer
            )
            answer_clean, pseudonymizer, _more_known = ticket._ai_pseudonymize(
                answer, pseudonymizer
            )
            # The residue is a stored compute on helpdesk.ai.qa: it is filled
            # by the create, with the strict check.
            created |= Qa.create(
                {
                    "question": question_clean,
                    "answer": answer_clean,
                    "source": "import",
                    "ticket_id": ticket.id,
                    "company_id": ticket.company_id.id,
                    "team_id": ticket.team_id.id,
                    "category_id": ticket.category_id.id,
                    "usage": Qa._pick_usage(ticket.id, self.test_share),
                }
            )
        if not created:
            raise UserError(
                _("None of the %s tickets found has a reply from the staff.", skipped)
            )
        return {
            "type": "ir.actions.act_window",
            "name": _("Imported Entries to Validate"),
            "res_model": "helpdesk.ai.qa",
            "view_mode": "list,form",
            "domain": [("id", "in", created.ids)],
        }
