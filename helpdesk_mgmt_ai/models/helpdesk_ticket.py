# Copyright 2026 Sergio Corato
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from markupsafe import Markup

from odoo import _, fields, models
from odoo.exceptions import AccessError, UserError
from odoo.tools import html2plaintext, plaintext2html

from ..tools.confidence import (
    adjust_level,
    extract_level_lines,
    is_abstention,
    parse_level,
)
from ..tools.pseudonymizer import Pseudonymizer, candidate_names, strip_legal_form
from .helpdesk_ai_draft_log import CONFIDENCE_LEVELS

_logger = logging.getLogger(__name__)

PARAM_PREFIX = "helpdesk_mgmt_ai_draft."
USER_GROUP = "helpdesk_mgmt_ai_draft.group_ai_draft_user"

AI_STATES = [
    ("none", "To prepare"),
    ("question_ready", "Question to approve"),
    ("sent", "Waiting for the model"),
    ("draft_ready", "Draft to review"),
    ("done", "Reviewed"),
    ("error", "Error"),
]

# Presidio entities -> placeholder labels
PRESIDIO_LABELS = {
    "PERSON": "PERSON",
    "LOCATION": "LOCATION",
    "EMAIL_ADDRESS": "EMAIL",
    "PHONE_NUMBER": "PHONE",
    "IBAN_CODE": "IBAN",
}

_presidio_analyzers = {}


def _get_presidio_analyzer(language, spacy_model):
    """Presidio analyzer, created once per language and model.

    Optional: requires presidio-analyzer and the spaCy model on the server.
    """
    key = (language, spacy_model)
    if key not in _presidio_analyzers:
        try:
            from presidio_analyzer import AnalyzerEngine
            from presidio_analyzer.nlp_engine import NlpEngineProvider

            provider = NlpEngineProvider(
                nlp_configuration={
                    "nlp_engine_name": "spacy",
                    "models": [{"lang_code": language, "model_name": spacy_model}],
                }
            )
            _presidio_analyzers[key] = AnalyzerEngine(
                nlp_engine=provider.create_engine(), supported_languages=[language]
            )
        except Exception as error:  # pylint: disable=broad-except
            _logger.warning("Presidio is not available: %s", error)
            _presidio_analyzers[key] = False
    return _presidio_analyzers[key]


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    ai_state = fields.Selection(
        AI_STATES,
        string="AI Assistant Status",
        default="none",
        required=True,
        copy=False,
        tracking=True,
    )
    ai_question_clean = fields.Text(
        string="Pseudonymized Question",
        copy=False,
        help="Text that will be sent to the model. The technician can correct "
        "or complete it (version, module, error message) before sending it.",
    )
    ai_placeholder_map = fields.Json(
        string="Placeholder Table",
        copy=False,
        groups=USER_GROUP,
        help="Mapping between placeholders and real data. It stays in Odoo only.",
    )
    ai_residue = fields.Text(
        string="Possible Remaining Personal Data", copy=False, readonly=True
    )
    ai_draft_clean = fields.Text(
        string="Pseudonymized Draft", copy=False, readonly=True
    )
    ai_draft = fields.Html(
        string="Draft Reply", copy=False, readonly=True, sanitize=True
    )
    ai_sources = fields.Html(string="Cited Sources", copy=False, readonly=True)
    ai_abstained = fields.Boolean(
        string="The Model Abstained", readonly=True, copy=False
    )
    ai_confidence_declared = fields.Selection(
        CONFIDENCE_LEVELS, string="Declared Confidence", readonly=True, copy=False
    )
    ai_confidence = fields.Selection(
        CONFIDENCE_LEVELS,
        string="Confidence",
        readonly=True,
        copy=False,
        help="Level declared by the model, lowered by the system when the "
        "citations are not verified or the sources found are not relevant enough.",
    )
    ai_confidence_reason = fields.Char(
        string="Confidence Reason", readonly=True, copy=False
    )
    ai_model_name = fields.Char(string="Model Used", readonly=True, copy=False)
    ai_execution_id = fields.Many2one(
        "ai.bridge.execution", string="Bridge Execution", readonly=True, copy=False
    )
    ai_error = fields.Text(string="AI Assistant Error", readonly=True, copy=False)
    ai_log_ids = fields.One2many(
        "helpdesk.ai.draft.log", "ticket_id", string="AI Draft Log"
    )

    # --- helpers ---------------------------------------------------------------

    def _ai_param(self, key, default=False):
        return (
            self.env["ir.config_parameter"].sudo().get_param(PARAM_PREFIX + key, default)
        )

    def _ai_check_user(self):
        if not self.env.user.has_group(USER_GROUP):
            raise AccessError(_("Only enabled technicians can use the AI assistant."))

    def _ai_source_text(self):
        self.ensure_one()
        description = html2plaintext(self.description or "")
        return f"{self.name or ''}\n\n{description}".strip()

    def _ai_partner_values(self, partner):
        """Values of a contact to search for and replace in the text."""
        label = "COMPANY" if partner.is_company else "PERSON"
        values = []
        name = (partner.name or "").strip()
        if name:
            values.append((label, name))
            short = strip_legal_form(name)
            if short:
                values.append((label, short))
            if not partner.is_company:
                # First name or surname alone, when long enough
                values += [(label, part) for part in name.split() if len(part) >= 4]
        for field_name, field_label in (
            ("email", "EMAIL"),
            ("phone", "PHONE"),
            ("mobile", "PHONE"),
            ("vat", "VAT"),
            ("l10n_it_codice_fiscale", "FISCALCODE"),
            ("l10n_it_pec_email", "EMAIL"),
            ("l10n_it_pa_index", "SDICODE"),
            ("street", "ADDRESS"),
        ):
            if field_name in partner._fields and partner[field_name]:
                values.append((field_label, str(partner[field_name])))
        return values

    def _ai_known_values(self, text):
        """(label, value) pairs known from Odoo for this ticket."""
        self.ensure_one()
        Partner = self.env["res.partner"].sudo()
        partners = Partner.browse()
        if self.partner_id:
            commercial = self.partner_id.sudo().commercial_partner_id
            partners |= self.partner_id.sudo() | commercial | commercial.child_ids
        # Names in the text that match existing contacts
        for candidate in candidate_names(text):
            variants = {candidate, strip_legal_form(candidate)} - {""}
            for variant in variants:
                found = Partner.search([("name", "=ilike", variant)], limit=1)
                if found:
                    partners |= found
        values = []
        for partner in partners:
            values += self._ai_partner_values(partner)
        if self.partner_name:
            values.append(("PERSON", self.partner_name))
        if self.partner_email:
            values.append(("EMAIL", self.partner_email))
        return values

    def _ai_presidio_values(self, text):
        if self._ai_param("use_presidio") not in ("1", "True", "true"):
            return []
        analyzer = _get_presidio_analyzer(
            self._ai_param("presidio_language", "it") or "it",
            self._ai_param("presidio_spacy_model", "it_core_news_lg") or "it_core_news_lg",
        )
        if not analyzer:
            return []
        try:
            min_score = float(self._ai_param("presidio_min_score", "0.6") or 0.6)
        except ValueError:
            min_score = 0.6
        results = analyzer.analyze(
            text=text,
            language=self._ai_param("presidio_language", "it") or "it",
            entities=list(PRESIDIO_LABELS),
        )
        values = []
        for result in results:
            value = text[result.start : result.end]
            if result.score >= min_score and "[" not in value:
                values.append((PRESIDIO_LABELS[result.entity_type], value))
        return values

    def _ai_pseudonymize(self, text, pseudonymizer=None):
        """Return (clean text, pseudonymizer, known values)."""
        self.ensure_one()
        pseudonymizer = pseudonymizer or Pseudonymizer()
        known = self._ai_known_values(self._ai_source_text() + "\n" + (text or ""))
        clean = pseudonymizer.pseudonymize(text, known)
        presidio = self._ai_presidio_values(clean)
        if presidio:
            clean = pseudonymizer.pseudonymize(clean, presidio)
            known += presidio
        return clean, pseudonymizer, known

    @staticmethod
    def _ai_format_residue(residue):
        return "\n".join(f"{label}: {value}" for label, value in residue) or False

    def _ai_get_bridge(self):
        self.ensure_one()
        bridges = (
            self.env["ai.bridge"]
            .sudo()
            .search(
                [
                    ("payload_type", "=", "helpdesk_question"),
                    ("model_id.model", "=", self._name),
                ]
            )
        )
        bridge = bridges.filtered(lambda b: b._enabled_for(self))[:1]
        if not bridge:
            raise UserError(
                _(
                    "No AI bridge is configured for tickets. Create a bridge with "
                    "model 'Helpdesk Ticket', payload type 'Helpdesk: pseudonymized "
                    "question' and result type 'Helpdesk: draft reply'."
                )
            )
        return bridge

    def _ai_installed_modules(self):
        modules = (
            self.env["ir.module.module"]
            .sudo()
            .search(
                [
                    ("state", "=", "installed"),
                    "|",
                    ("name", "=like", "l10n_it%"),
                    ("name", "=like", "account%"),
                ]
            )
        )
        return sorted(modules.mapped("name"))

    def _ai_prepare_bridge_payload(self):
        """Data sent to the external system: no personal data."""
        self.ensure_one()
        return {
            "question": self.ai_question_clean or "",
            "ticket": f"TICKET-{self.id}",
            "language": self.sudo().partner_id.lang or self.env.lang or "en_US",
            "odoo": {"version": "18.0", "edition": "community"},
            "installed_modules": self._ai_installed_modules(),
            "abstention_text": self._ai_param("abstention_text", ""),
            "confidence_levels": ["high", "medium", "low"],
        }

    def _ai_format_sources(self, sources):
        if not sources:
            return False
        items = []
        for source in sources:
            if isinstance(source, dict):
                ref = source.get("ref") or ""
                title = source.get("title") or source.get("url") or ref
                url = source.get("url") or ""
                label = f"[{ref}] {title}" if ref else title
                if url.startswith(("https://", "http://")):
                    items.append(
                        Markup('<li><a href="%s" target="_blank">%s</a></li>')
                        % (url, label)
                    )
                else:
                    items.append(Markup("<li>%s</li>") % label)
            else:
                items.append(Markup("<li>%s</li>") % str(source))
        return Markup("<ul>%s</ul>") % Markup("").join(items)

    def _ai_reset_draft_values(self):
        return {
            "ai_draft_clean": False,
            "ai_draft": False,
            "ai_sources": False,
            "ai_abstained": False,
            "ai_confidence_declared": False,
            "ai_confidence": False,
            "ai_confidence_reason": False,
            "ai_model_name": False,
            "ai_execution_id": False,
            "ai_error": False,
        }

    # --- technician actions -------------------------------------------------------

    def action_ai_prepare_question(self):
        """Step 1: clean the ticket text and propose it to the technician."""
        self._ai_check_user()
        for ticket in self:
            if ticket.ai_state in ("sent", "draft_ready"):
                raise UserError(
                    _("Ticket %s already has a draft in progress.", ticket.display_name)
                )
            clean, pseudonymizer, known = ticket._ai_pseudonymize(
                ticket._ai_source_text()
            )
            residue = pseudonymizer.residue(clean, known)
            values = ticket._ai_reset_draft_values()
            values.update(
                {
                    "ai_question_clean": clean,
                    "ai_placeholder_map": pseudonymizer.mapping,
                    "ai_residue": ticket._ai_format_residue(residue),
                    "ai_state": "question_ready",
                }
            )
            ticket.write(values)
        return True

    def action_ai_send_question(self):
        """Step 2: the technician approves the question and sends it to the model."""
        self.ensure_one()
        self._ai_check_user()
        if self.ai_state != "question_ready":
            raise UserError(_("Prepare the question first with 'Prepare AI draft'."))
        question = (self.ai_question_clean or "").strip()
        if not question:
            raise UserError(_("The question to send is empty."))
        # The technician may have edited the text: check everything again.
        pseudonymizer = Pseudonymizer(self.ai_placeholder_map or {})
        clean, pseudonymizer, known = self._ai_pseudonymize(question, pseudonymizer)
        residue = pseudonymizer.residue(clean, known)
        if residue:
            self.write(
                {
                    "ai_question_clean": clean,
                    "ai_placeholder_map": pseudonymizer.mapping,
                    "ai_residue": self._ai_format_residue(residue),
                }
            )
            raise UserError(
                _(
                    "Sending blocked: the question may still contain personal data.\n"
                    "%s\nCorrect the text and try again.",
                    self._ai_format_residue(residue),
                )
            )
        bridge = self._ai_get_bridge()
        self.write(
            {
                "ai_question_clean": clean,
                "ai_placeholder_map": pseudonymizer.mapping,
                "ai_residue": False,
                "ai_state": "sent",
                "ai_error": False,
            }
        )
        Execution = self.env["ai.bridge.execution"].sudo()
        domain = [
            ("ai_bridge_id", "=", bridge.id),
            ("res_id", "=", self.id),
            ("model_id.model", "=", self._name),
        ]
        last_before = Execution.search(domain, order="id desc", limit=1).id or 0
        bridge.execute_ai_bridge(self._name, self.id)
        execution = Execution.search(
            domain + [("id", ">", last_before)], order="id desc", limit=1
        )
        if not execution:
            # The bridge did not start (disabled or not allowed for this user)
            self.write({"ai_state": "question_ready"})
            raise UserError(
                _("The bridge '%s' is not available for your user.", bridge.display_name)
            )
        if execution.state == "error":
            self.write(
                {
                    "ai_state": "error",
                    "ai_execution_id": execution.id,
                    "ai_error": _(
                        "The call to the model failed. See the details in the "
                        "bridge execution '%s'.",
                        execution.display_name,
                    ),
                }
            )
        message = {
            "draft_ready": _("The draft is ready to review."),
            "sent": _("Question sent: the draft will arrive as soon as it is ready."),
            "error": _("The call to the model failed."),
        }.get(self.ai_state, _("Question sent."))
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "message": message,
                "type": "danger" if self.ai_state == "error" else "info",
                "next": {"type": "ir.actions.client", "tag": "soft_reload"},
            },
        }

    def action_ai_open_review(self):
        """Step 3: open the review of the draft."""
        self.ensure_one()
        self._ai_check_user()
        if self.ai_state != "draft_ready":
            raise UserError(_("There is no draft to review."))
        return {
            "type": "ir.actions.act_window",
            "name": _("Review AI Draft"),
            "res_model": "helpdesk.ai.review.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_ticket_id": self.id},
        }

    def action_ai_reset(self):
        """Bring the assistant back to the initial state (after an error or a change of mind)."""
        self._ai_check_user()
        values = self._ai_reset_draft_values()
        values.update(
            {
                "ai_state": "none",
                "ai_question_clean": False,
                "ai_placeholder_map": False,
                "ai_residue": False,
            }
        )
        self.write(values)
        return True

    # --- model reply --------------------------------------------------------------

    def _ai_receive_draft(self, data, execution=False):
        """Store the draft received from the external system.

        Expected format (JSON):
        {
            "answer": "text with placeholders and citations [F1]",
            "abstained": false,
            "confidence": "high|medium|low",
            "confidence_reason": "...",
            "sources": [{"ref": "F1", "title": "...", "url": "https://..."}],
            "citations_verified": true,
            "retrieval_score": 0.82,
            "model": "model name"
        }
        When the fields are missing, level and reason are read from the
        CONFIDENCE: and REASON: lines at the end of the answer.
        """
        self.ensure_one()
        ticket = self.sudo()
        if not isinstance(data, dict):
            data = {"answer": str(data or "")}
        answer = data.get("answer") or data.get("body") or ""
        answer, line_level, line_reason = extract_level_lines(answer)
        declared = parse_level(data.get("confidence")) or line_level
        reason = data.get("confidence_reason") or line_reason or False
        abstention_text = ticket._ai_param("abstention_text", "")
        abstained = bool(data.get("abstained")) or is_abstention(answer, abstention_text)
        try:
            min_score = float(ticket._ai_param("min_retrieval_score", "0") or 0)
        except ValueError:
            min_score = 0.0
        final = False
        if not abstained:
            final = adjust_level(
                declared,
                citations_verified=data.get("citations_verified"),
                retrieval_score=data.get("retrieval_score"),
                min_score=min_score,
            )
        pseudonymizer = Pseudonymizer(ticket.ai_placeholder_map or {})
        restored = pseudonymizer.restore(answer)
        draft_html = plaintext2html(restored)
        ticket.write(
            {
                "ai_draft_clean": answer,
                "ai_draft": draft_html,
                "ai_sources": ticket._ai_format_sources(data.get("sources")),
                "ai_abstained": abstained,
                "ai_confidence_declared": declared or False,
                "ai_confidence": final,
                "ai_confidence_reason": reason,
                "ai_model_name": data.get("model") or False,
                "ai_execution_id": execution.id if execution else False,
                "ai_state": "draft_ready",
                "ai_error": False,
            }
        )
        if abstained:
            heading = _("AI draft: the model did not find enough sources.")
        else:
            level_label = dict(
                ticket._fields["ai_confidence"]._description_selection(ticket.env)
            ).get(final, "-")
            heading = _("AI draft to review. Confidence: %s", level_label)
        body = Markup("<p><strong>%s</strong></p>%s") % (heading, draft_html)
        # Internal note: the customer does not see it.
        ticket.message_post(
            body=body, message_type="comment", subtype_xmlid="mail.mt_note"
        )
        return True
