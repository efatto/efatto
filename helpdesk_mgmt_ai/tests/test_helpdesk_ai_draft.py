# Copyright 2026 Sergio Corato
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests import Form, TransactionCase, new_test_user


class TestHelpdeskAiDraft(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.technician = new_test_user(
            cls.env,
            login="ai_technician",
            groups="base.group_user,helpdesk_mgmt.group_helpdesk_user,"
            "helpdesk_mgmt_ai_draft.group_ai_draft_user",
        )
        cls.manager = new_test_user(
            cls.env,
            login="ai_manager",
            groups="base.group_user,helpdesk_mgmt.group_helpdesk_manager,"
            "helpdesk_mgmt_ai_draft.group_ai_draft_manager",
        )
        cls.company_partner = cls.env["res.partner"].create(
            {"name": "Rossi Impianti Srl", "is_company": True, "vat": "IT01234567890"}
        )
        cls.contact = cls.env["res.partner"].create(
            {
                "name": "Mario Rossi",
                "parent_id": cls.company_partner.id,
                "email": "mario.rossi@rossi-impianti.it",
                "phone": "347 123 4567",
            }
        )
        cls.ticket = cls.env["helpdesk.ticket"].create(
            {
                "name": "Fattura scartata",
                "partner_id": cls.contact.id,
                "description": "<p>Sono Mario Rossi di Rossi Impianti Srl, la "
                "fattura FT/2026/00145 è stata scartata. Il mio numero è "
                "347 123 4567.</p>",
            }
        )
        cls.reason_wrong = cls.env.ref("helpdesk_mgmt_ai_draft.reason_wrong")

    def _ticket(self):
        return self.ticket.with_user(self.technician)

    def test_prepare_question(self):
        ticket = self._ticket()
        ticket.action_ai_prepare_question()
        self.assertEqual(ticket.ai_state, "question_ready")
        question = ticket.ai_question_clean
        self.assertNotIn("Rossi", question)
        self.assertNotIn("347", question)
        self.assertNotIn("FT/2026/00145", question)
        self.assertFalse(ticket.ai_residue)

    def test_edited_question_is_checked_again(self):
        ticket = self._ticket()
        ticket.action_ai_prepare_question()
        edited = ticket.ai_question_clean + "\nRicontattare luigi@example.com"
        clean, _pseudonymizer, _known = ticket._ai_pseudonymize(edited)
        self.assertNotIn("luigi@example.com", clean)

    def test_send_without_bridge(self):
        ticket = self._ticket()
        ticket.action_ai_prepare_question()
        with self.assertRaises(UserError):
            ticket.action_ai_send_question()

    def _receive(self, ticket, **data):
        values = {
            "answer": "Gentile [PERSON_1], apra la fattura e prema 'Invia a SdI' [F1].",
            "confidence": "high",
            "confidence_reason": "standard procedure",
            "sources": [
                {"ref": "F1", "title": "Odoo 18 documentation", "url": "https://www.odoo.com"}
            ],
            "citations_verified": True,
            "model": "test-model",
        }
        values.update(data)
        ticket.sudo()._ai_receive_draft(values)

    def test_receive_draft_and_restore(self):
        ticket = self._ticket()
        ticket.action_ai_prepare_question()
        ticket.write({"ai_state": "sent"})
        self._receive(ticket)
        self.assertEqual(ticket.ai_state, "draft_ready")
        self.assertEqual(ticket.ai_confidence, "high")
        self.assertIn("Mario Rossi", ticket.ai_draft)
        self.assertNotIn("Mario Rossi", ticket.ai_draft_clean)

    def test_unverified_citations_lower_confidence(self):
        ticket = self._ticket()
        ticket.action_ai_prepare_question()
        self._receive(ticket, citations_verified=False)
        self.assertEqual(ticket.ai_confidence_declared, "high")
        self.assertEqual(ticket.ai_confidence, "low")

    def test_level_lines_in_answer(self):
        ticket = self._ticket()
        ticket.action_ai_prepare_question()
        self._receive(
            ticket,
            answer="Step 1 [F1]\nCONFIDENCE: LOW\nREASON: indirect source",
            confidence=None,
            confidence_reason=None,
        )
        self.assertEqual(ticket.ai_confidence, "low")
        self.assertEqual(ticket.ai_confidence_reason, "indirect source")
        self.assertNotIn("CONFIDENCE", ticket.ai_draft_clean)

    def _review(self, ticket, outcome):
        wizard_form = Form(
            self.env["helpdesk.ai.review.wizard"]
            .with_user(self.technician)
            .with_context(default_ticket_id=ticket.id)
        )
        wizard_form.outcome = outcome
        return wizard_form.save()

    def test_review_approved_feeds_archive(self):
        ticket = self._ticket()
        ticket.action_ai_prepare_question()
        self._receive(ticket)
        wizard = self._review(ticket, "approved")
        wizard.action_confirm()
        self.assertEqual(ticket.ai_state, "done")
        log = ticket.ai_log_ids
        self.assertEqual(log.outcome, "approved")
        self.assertTrue(log.sent_to_customer)
        self.assertNotIn("Mario Rossi", log.final_answer_clean)
        qa = self.env["helpdesk.ai.qa"].search([("ticket_id", "=", ticket.id)])
        self.assertEqual(qa.source, "review")
        self.assertEqual(qa.state, "validated")
        self.assertNotIn("Rossi", qa.question + qa.answer)

    def test_review_modified_requires_reason(self):
        ticket = self._ticket()
        ticket.action_ai_prepare_question()
        self._receive(ticket)
        wizard = (
            self.env["helpdesk.ai.review.wizard"]
            .with_user(self.technician)
            .create(
                {
                    "ticket_id": ticket.id,
                    "outcome": "approved",
                    "answer": "<p>Text changed by the technician</p>",
                }
            )
        )
        # Approved but with a different text: counts as modified, needs a reason
        with self.assertRaises(UserError):
            wizard.action_confirm()
        wizard.reason_id = self.reason_wrong
        wizard.action_confirm()
        self.assertEqual(ticket.ai_log_ids.outcome, "modified")
        self.assertEqual(ticket.ai_log_ids.reason_id, self.reason_wrong)

    def test_review_rejected_other_requires_note(self):
        ticket = self._ticket()
        ticket.action_ai_prepare_question()
        self._receive(ticket)
        other = self.env.ref("helpdesk_mgmt_ai_draft.reason_other")
        wizard = (
            self.env["helpdesk.ai.review.wizard"]
            .with_user(self.technician)
            .create({"ticket_id": ticket.id, "outcome": "rejected", "reason_id": other.id})
        )
        with self.assertRaises(UserError):
            wizard.action_confirm()
        wizard.note = "Answer for version 16"
        wizard.action_confirm()
        log = ticket.ai_log_ids
        self.assertEqual(log.outcome, "rejected")
        self.assertFalse(log.sent_to_customer)
        self.assertFalse(
            self.env["helpdesk.ai.qa"].search([("ticket_id", "=", ticket.id)])
        )

    def test_bridge_payload_has_no_personal_data(self):
        ticket = self._ticket()
        ticket.action_ai_prepare_question()
        payload = ticket._ai_prepare_bridge_payload()
        text = str(payload)
        for value in ("Rossi", "mario.rossi", "347 123 4567", "01234567890"):
            self.assertNotIn(value, text)
        self.assertEqual(payload["odoo"]["version"], "18.0")

    def _solved_ticket(self):
        ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "Nota di credito",
                "partner_id": self.contact.id,
                "description": "<p>Sono Mario Rossi: come annullo una fattura "
                "confermata?</p>",
            }
        )
        ticket.message_post(
            body="<p>Gentile Mario Rossi, usi il pulsante Nota di credito.</p>",
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
            author_id=self.env.user.partner_id.id,
        )
        Stage = self.env["helpdesk.ticket.stage"]
        values = {"name": "Solved for test"}
        if "closed" in Stage._fields:
            values["closed"] = True
        ticket.stage_id = Stage.create(values)
        if "closed_date" in ticket._fields and not ticket.closed_date:
            ticket.closed_date = ticket.create_date
        return ticket

    def test_import_solved_tickets(self):
        ticket = self._solved_ticket()
        wizard = (
            self.env["helpdesk.ai.qa.import.wizard"]
            .with_user(self.manager)
            .create({"answer_mode": "last", "test_share": 0})
        )
        self.assertGreaterEqual(wizard.ticket_count, 1)
        wizard.action_import()
        qa = self.env["helpdesk.ai.qa"].search([("ticket_id", "=", ticket.id)])
        self.assertEqual(qa.source, "import")
        self.assertEqual(qa.state, "to_validate")
        self.assertEqual(qa.usage, "knowledge")
        self.assertIn("Nota di credito", qa.answer)
        self.assertNotIn("Rossi", qa.question + qa.answer)
        # A second import skips tickets already in the archive
        wizard_again = (
            self.env["helpdesk.ai.qa.import.wizard"].with_user(self.manager).create({})
        )
        self.assertNotIn(ticket, self.env["helpdesk.ticket"].search(
            wizard_again._ticket_domain()
        ))
        qa.with_user(self.manager).action_validate()
        self.assertEqual(qa.state, "validated")
        action = qa.with_user(self.manager).action_export_jsonl()
        self.assertEqual(action["type"], "ir.actions.act_url")

    def test_validation_blocked_on_residue(self):
        qa = self.env["helpdesk.ai.qa"].create(
            {"question": "Domanda", "answer": "Scrivere a luigi@example.com"}
        )
        with self.assertRaises(UserError):
            qa.with_user(self.manager).action_validate()
        self.assertTrue(qa.has_residue)
