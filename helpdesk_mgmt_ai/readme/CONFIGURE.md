**Groups.** Give technicians the group *Helpdesk AI Assistant / Technician*.
The *Manager* group validates the archive, imports solved tickets and manages
the review reasons.

**AI bridge.** In *AI Bridge* create a bridge with:

- Model: *Helpdesk Ticket* (`helpdesk.ticket`)
- Payload type: *Helpdesk: pseudonymized question*
- Result type: *Helpdesk: draft reply*
- Result mode (immediate or asynchronous), URL and authentication of the
  external system

Odoo sends this payload (plus the `_odoo` fields and, for asynchronous calls,
the `_response_url` added by `ai_oca_bridge`):

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

- export them from the archive list (action *Export for the AI (JSONL)*) and
  load the file into the RAG index;
- read the model `helpdesk.ai.qa` through the Odoo API with a dedicated user,
  filtering `state = validated` and `usage = knowledge`.

Never index the *test set* entries.

**System parameters** (`helpdesk_mgmt_ai_draft.*`):

- `abstention_text`: fixed text the model uses to abstain. Keep it in the
  language of the system prompt.
- `min_retrieval_score`: threshold on the source score; `0` disables it. Set
  it after looking at the real scores.
- `test_share_percent`: share of new archive entries kept for the test set
  (default 20).
- `auto_validate_reviewed`: `True` to validate automatically the replies
  approved by a technician.
- `use_presidio`: `True` to add the recognition of names and places with
  Microsoft Presidio (requires `presidio-analyzer` and the spaCy model on the
  Odoo server).
- `presidio_language`, `presidio_spacy_model`, `presidio_min_score`:
  Presidio language (`it`), spaCy model (`it_core_news_lg`) and minimum
  entity score (0.6).
