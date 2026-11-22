# Copyright 2026 Sergio Corato
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64

from odoo.exceptions import AccessError, UserError, ValidationError
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
            "helpdesk_mgmt_ai.group_ai_draft_user",
        )
        cls.manager = new_test_user(
            cls.env,
            login="ai_manager",
            groups="base.group_user,helpdesk_mgmt.group_helpdesk_manager,"
            "helpdesk_mgmt_ai.group_ai_draft_manager",
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
        cls.reason_wrong = cls.env.ref("helpdesk_mgmt_ai.reason_wrong")

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
                {
                    "ref": "F1",
                    "title": "Odoo 18 documentation",
                    "url": "https://www.odoo.com",
                }
            ],
            "citations_verified": True,
            "model": "test-model",
        }
        values.update(data)
        if ticket.ai_state != "sent":
            ticket.write({"ai_state": "sent"})
        return ticket.sudo()._ai_receive_draft(values)

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
        # auto_validate_reviewed is off by default: the entry needs a manager
        self.assertEqual(qa.state, "to_validate")
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
        other = self.env.ref("helpdesk_mgmt_ai.reason_other")
        wizard = (
            self.env["helpdesk.ai.review.wizard"]
            .with_user(self.technician)
            .create(
                {"ticket_id": ticket.id, "outcome": "rejected", "reason_id": other.id}
            )
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
        ticket.write({"ai_state": "sent", "ai_personal_data_checked": True})
        payload = ticket._ai_prepare_bridge_payload()
        text = str(payload)
        for value in ("Rossi", "mario.rossi", "347 123 4567", "01234567890"):
            self.assertNotIn(value, text)
        self.assertEqual(payload["odoo"]["version"], "18.0")

    # --- gate, bridge and response handling -----------------------------------

    def _bridge(self, **values):
        vals = {
            "name": "Helpdesk bridge",
            "payload_type": "helpdesk_question",
            "result_type": "helpdesk_draft",
            "model_id": self.env["ir.model"]._get_id("helpdesk.ticket"),
            "url": "https://example.invalid/ai",
        }
        vals.update(values)
        return self.env["ai.bridge"].create(vals)

    def test_bridge_sample_payload_does_not_raise(self):
        """The bridge form computes the sample payload with no record."""
        bridge = self._bridge()
        payload = bridge.with_context(sample_payload=True)._prepare_payload()
        self.assertIn("question", payload)

    def test_bridge_cannot_be_automatic(self):
        with self.assertRaises(ValidationError):
            self._bridge(usage="ai_thread_write")

    def test_payload_builder_requires_the_approved_question(self):
        """A direct execute_ai_bridge must not send an unapproved text."""
        bridge = self._bridge()
        ticket = self._ticket()
        ticket.action_ai_prepare_question()
        with self.assertRaises(UserError):
            bridge._prepare_payload(record=ticket)
        ticket.write({"ai_state": "sent", "ai_personal_data_checked": True})
        self.assertTrue(bridge._prepare_payload(record=ticket)["question"])

    def test_personal_data_confirmation_is_required(self):
        ticket = self._ticket()
        ticket.action_ai_prepare_question()
        with self.assertRaises(UserError):
            ticket.action_ai_send_question()
        ticket.ai_personal_data_checked = True
        with self.assertRaises(UserError) as error:
            ticket.action_ai_send_question()
        # the confirmation passed: the next failure is the missing bridge
        self.assertIn("bridge", str(error.exception).lower())

    def test_send_blocked_on_residue(self):
        # A bridge must exist: without it the test would pass on the "no
        # bridge" error instead of on the residue check.
        self._bridge()
        ticket = self._ticket()
        ticket.action_ai_prepare_question()
        # E-mail and phone are masked before sending, so the block comes from
        # the strict check: a run of digits no pattern recognises.
        ticket.write(
            {
                "ai_question_clean": ticket.ai_question_clean
                + "\nRiferimento ordine 123456789",
                "ai_personal_data_checked": True,
            }
        )
        # stored compute: it survives the rollback of the failing action
        self.assertTrue(ticket.ai_residue)
        with self.assertRaises(UserError) as error:
            ticket.action_ai_send_question()
        self.assertIn("personal data", str(error.exception).lower())
        self.assertTrue(ticket.ai_residue)
        self.assertEqual(ticket.ai_state, "question_ready")

    def test_gate_requires_the_ai_group(self):
        """Any user may write ai_state: the gate must check the group."""
        outsider = new_test_user(
            self.env,
            login="ai_outsider",
            groups="base.group_user,helpdesk_mgmt.group_helpdesk_user",
        )
        bridge = self._bridge()
        ticket = self._ticket()
        ticket.action_ai_prepare_question()
        ticket.write({"ai_state": "sent", "ai_personal_data_checked": True})
        with self.assertRaises(AccessError):
            bridge._prepare_payload(record=ticket.with_user(outsider))

    def test_bridge_must_belong_to_the_company(self):
        other = self.env["res.company"].create({"name": "Bridge company"})
        self._bridge(company_id=other.id)
        ticket = self._ticket()
        with self.assertRaises(UserError):
            ticket._ai_get_bridge()

    def test_stale_execution_is_ignored(self):
        bridge = self._bridge()
        ticket = self._ticket()
        ticket.action_ai_prepare_question()
        Execution = self.env["ai.bridge.execution"]
        model_id = self.env["ir.model"]._get_id("helpdesk.ticket")
        first = Execution.create(
            {
                "ai_bridge_id": bridge.id,
                "model_id": model_id,
                "res_id": ticket.id,
                "payload": {"question": ticket.ai_question_clean},
            }
        )
        second = Execution.create(
            {
                "ai_bridge_id": bridge.id,
                "model_id": model_id,
                "res_id": ticket.id,
                "payload": {"question": "another question"},
            }
        )
        ticket.write({"ai_state": "sent", "ai_execution_id": first.id})
        self.assertFalse(
            ticket.sudo()._ai_receive_draft({"answer": "x"}, execution=second)
        )
        self.assertEqual(ticket.ai_state, "sent")

    def test_draft_for_another_question_is_ignored(self):
        bridge = self._bridge()
        ticket = self._ticket()
        ticket.action_ai_prepare_question()
        execution = self.env["ai.bridge.execution"].create(
            {
                "ai_bridge_id": bridge.id,
                "model_id": self.env["ir.model"]._get_id("helpdesk.ticket"),
                "res_id": ticket.id,
                "payload": {"question": "a question that was never sent"},
            }
        )
        ticket.write({"ai_state": "sent", "ai_execution_id": execution.id})
        self.assertFalse(
            ticket.sudo()._ai_receive_draft({"answer": "x"}, execution=execution)
        )

    def test_known_placeholder_in_the_reply_is_refused(self):
        """A known [PERSON_1] left in the reply would reach the customer."""
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
                    "answer": "<p>Gentile [PERSON_1], fatto.</p>",
                }
            )
        )
        with self.assertRaises(UserError):
            wizard.action_confirm()

    def test_export_rechecks_the_residue(self):
        """A contact created after the entry makes the stored residue stale."""
        Qa = self.env["helpdesk.ai.qa"]
        entry = Qa.create(
            {
                "question": "Nota di credito",
                "answer": "Luigi Verdi ha scritto",
                "ticket_id": self.ticket.id,
            }
        )
        entry.action_validate()
        self.assertFalse(entry.has_residue)
        self.env["res.partner"].create({"name": "Luigi Verdi"})
        with self.assertRaises(UserError):
            entry.action_export_jsonl()

    def test_draft_ignored_when_not_sent(self):
        ticket = self._ticket()
        ticket.action_ai_prepare_question()
        self.assertFalse(ticket._ai_receive_draft({"answer": "testo"}))
        self.assertNotEqual(ticket.ai_state, "draft_ready")

    def test_string_false_is_not_an_abstention(self):
        ticket = self._ticket()
        ticket.action_ai_prepare_question()
        self._receive(ticket, abstained="false")
        self.assertFalse(ticket.ai_abstained)
        self.assertEqual(ticket.ai_confidence, "high")

    def test_unverified_citations_as_string(self):
        ticket = self._ticket()
        ticket.action_ai_prepare_question()
        self._receive(ticket, citations_verified="false")
        self.assertEqual(ticket.ai_confidence, "low")

    def test_unresolved_placeholder_blocks_the_reply(self):
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
                    "answer": "<p>Gentile [PERSON_9], fatto.</p>",
                }
            )
        )
        with self.assertRaises(UserError):
            wizard.action_confirm()

    def test_note_is_pseudonymized_in_the_log(self):
        ticket = self._ticket()
        ticket.action_ai_prepare_question()
        self._receive(ticket)
        reason = self.env.ref("helpdesk_mgmt_ai.reason_personal_data")
        wizard = (
            self.env["helpdesk.ai.review.wizard"]
            .with_user(self.technician)
            .create(
                {
                    "ticket_id": ticket.id,
                    "outcome": "rejected",
                    "reason_id": reason.id,
                    "note": "Mario Rossi 347 123 4567 era ancora nel testo",
                }
            )
        )
        wizard.action_confirm()
        note = ticket.ai_log_ids.note
        self.assertNotIn("Mario", note)
        self.assertNotIn("347", note)

    def test_staff_reply_from_a_bot_is_imported(self):
        ticket = self._solved_ticket()
        ticket.message_post(
            body="<p>Risposta automatica dello studio.</p>",
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
            author_id=self.env.ref("base.partner_root").id,
        )
        wizard = (
            self.env["helpdesk.ai.qa.import.wizard"]
            .with_user(self.manager)
            .create({"answer_mode": "last", "test_share": 0})
        )
        wizard.action_import()
        qa = self.env["helpdesk.ai.qa"].search([("ticket_id", "=", ticket.id)])
        self.assertIn("Risposta automatica", qa.answer)

    def test_export_only_the_requested_usage(self):
        Qa = self.env["helpdesk.ai.qa"]
        knowledge = Qa.create({"question": "Q1", "answer": "A1", "usage": "knowledge"})
        test = Qa.create({"question": "Q2", "answer": "A2", "usage": "test"})
        (knowledge | test).action_validate()
        (knowledge | test).action_export_jsonl(usage="knowledge")
        attachment = self.env["ir.attachment"].search(
            [("res_model", "=", Qa._name)], order="id desc", limit=1
        )
        content = base64.b64decode(attachment.datas).decode()
        self.assertIn(f"QA-{knowledge.id}", content)
        self.assertNotIn(f"QA-{test.id}", content)

    def test_qa_entry_visible_only_in_its_company(self):
        company_b = self.env["res.company"].create({"name": "Other company"})
        Qa = self.env["helpdesk.ai.qa"]
        qa_a = Qa.create({"question": "A", "answer": "A"})
        qa_b = Qa.create({"question": "B", "answer": "B", "company_id": company_b.id})
        visible = (
            Qa.with_user(self.manager)
            .with_company(self.env.company)
            .search([("id", "in", (qa_a | qa_b).ids)])
        )
        self.assertEqual(visible, qa_a)

    def test_import_wizard_validates_its_inputs(self):
        Wizard = self.env["helpdesk.ai.qa.import.wizard"].with_user(self.manager)
        with self.assertRaises(UserError):
            Wizard.create({"test_share": 150})
        with self.assertRaises(UserError):
            Wizard.create({"limit": 0})

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
            author_id=self.technician.partner_id.id,
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
        self.assertNotIn(
            ticket, self.env["helpdesk.ticket"].search(wizard_again._ticket_domain())
        )
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
