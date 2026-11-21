**Groups.** Give technicians the group *Helpdesk AI Assistant / Technician*.
The *Manager* group validates the archive, imports solved tickets and manages
the review reasons. The draft log is write-once: no group can edit or delete
it, so the metrics cannot be changed after the fact.

**AI bridge.** In *AI Bridge* create a bridge with:

- Model: *Helpdesk Ticket* (`helpdesk.ticket`)
- Payload type: *Helpdesk: pseudonymized question*
- Result type: *Helpdesk: draft reply*
- Result mode (immediate or asynchronous), URL and authentication of the
  external system

The bridge usage must stay *None*: the question is sent by the ticket buttons,
never automatically (a constraint refuses an automatic usage).

Do not create a bridge with payload type *Record* on *Helpdesk Ticket*: that
payload sends the fields of the ticket as they are (description, contact,
chatter) and defeats the pseudonymization. Use it only on models without
personal data.

Odoo sends this payload (plus `_odoo` and, for asynchronous calls, the
`_response_url` added by `ai_oca_bridge`). For this payload type the module
removes `db_name` and `user_id` from `_odoo`, because the database name is
usually the customer's name: only `db` (the uuid) and `db_hash` remain.

```json
{
  "question": "Pseudonymized text approved by the technician",
  "ticket": "TICKET-42",
  "language": "it_IT",
  "odoo": {"version": "18.0", "edition": "community"},
  "installed_modules": ["account", "l10n_it", "l10n_it_edi"],
  "abstention_text": "I have no verified information to answer.",
  "confidence_levels": ["high", "medium", "low"]
}
```

The external system must reply (immediately or on `_response_url`) with:

```json
{
  "answer": "Text with the placeholders and the citations [F1]",
  "abstained": false,
  "confidence": "high",
  "confidence_reason": "Every step has a source for version 18",
  "sources": [{"ref": "F1", "title": "Odoo 18 - Italy", "url": "https://..."}],
  "citations_verified": true,
  "retrieval_score": 0.82,
  "model": "model name"
}
```

When `confidence` and `confidence_reason` are missing, the module reads the
`CONFIDENCE:` and `REASON:` lines (or the Italian `AFFIDABILITA:` and
`MOTIVO:`) at the end of `answer`. The final level can only go down: it
becomes *low* when `citations_verified` is `false` and drops one step when
`retrieval_score` is below the threshold.

**Q&A archive for the AI.** The external system can read the validated
*knowledge base* entries in two ways:

- export them from the archive list (actions *Export the knowledge base for
  the AI (JSONL)* and *Export the test set (JSONL)*, which never mix) and load
  the file into the RAG index;
- read the model `helpdesk.ai.qa` through the Odoo API with a dedicated user,
  filtering `state = validated` and `usage = knowledge`.

Never index the *test set* entries.

**System parameters** (`helpdesk_mgmt_ai.*`):

- `abstention_text`: fixed text the model uses to abstain. Keep it in the
  language of the system prompt.
- `min_retrieval_score`: threshold on the source score; `0` disables it. Set
  it after looking at the real scores.
- `test_share_percent`: share of new archive entries kept for the test set
  (default 20).
- `auto_validate_reviewed`: `True` to validate automatically the replies
  approved by a technician. Off by default: the entry is the material the
  model cites, so it deserves a second pair of eyes.
- `use_presidio`: `True` to add the recognition of names and places with
  Microsoft Presidio (requires `presidio-analyzer` and the spaCy model on the
  Odoo server). When it is on and the library or the model is missing, sending
  is blocked instead of silently degrading name detection.
- `presidio_language`, `presidio_spacy_model`, `presidio_min_score`:
  Presidio language (`it`), spaCy model (`it_core_news_lg`) and minimum
  entity score (0.6).
