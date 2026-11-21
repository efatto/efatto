- Pseudonymization is not perfect: a name that is not stored as a contact,
  a misspelled name, a nickname or a detail that identifies a person by
  context can slip through. The automatic check covers formats (e-mail,
  phone, IBAN, VAT, fiscal code, SdI code, document numbers, URLs), values of
  known contacts, a leftover `@`, runs of 9+ digits and query strings; the
  technician confirms the rest with a checkbox.
- The archive keeps `[PERSON_1]` numbering per entry, so two entries about the
  same person can share a placeholder: add a per-entry suffix if the archive
  is ever shared outside the company.
- Ticket attachments are not sent.
- Only the initial ticket text (subject and description) is used, not the
  following messages.
- Automatic sync of the validated archive with the RAG index, instead of the
  JSONL export.
