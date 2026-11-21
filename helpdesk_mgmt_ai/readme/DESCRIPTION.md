Prepares draft replies to helpdesk tickets with an AI model, without sending
personal data to the model and without anything reaching the customer before
a technician approves it.

The flow has two approvals:

1. **Question.** The ticket text is pseudonymized in Odoo: names, companies,
   emails, phone numbers, VAT numbers, Italian fiscal codes, IBANs, SdI
   recipient codes and document numbers become placeholders such as
   `[PERSON_1]` or `[EMAIL_1]`. The technician checks and completes the
   question, then sends it. If personal data may still be present, sending
   is blocked.
2. **Reply.** The draft comes back with the cited sources and a confidence
   level (high, medium, low). Odoo puts the real data back in place of the
   placeholders and posts the draft as an internal note. The technician
   approves, modifies or rejects it; modifying or rejecting requires a
   reason.

Every review is stored in the draft log, pseudonymized only, to measure
precision.

The module also keeps a **question and answer archive**, the material that
extends what the AI can answer:

- replies approved by a technician enter it automatically;
- a wizard retrieves already solved tickets (question plus staff reply),
  pseudonymized and to be validated by a manager;
- each entry is either *knowledge base* (indexed by the external AI system as
  a source it can cite) or *test set* (kept out of the knowledge base and used
  only to measure precision);
- validated entries can be exported as JSON Lines for the RAG index.

The connection to the model goes through the OCA module `ai_oca_bridge`:
Odoo sends the question to an external system (for example n8n or a RAG
service), which queries the model and returns the draft.

Last updated: 2026-11-21.
