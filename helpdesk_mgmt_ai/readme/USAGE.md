**Draft replies**

1. Open a ticket and press **Prepare AI draft**. The *AI Assistant* tab shows
   the pseudonymized question.
2. Check the question. You can complete it with version, module and error
   message. Tick **I checked the question for personal data** and press
   **Approve and send the question**. If the automatic check still finds a
   value, the send is refused and the values are listed in the AI tab. Names
   that are not stored as a contact in Odoo are not detected: they are what
   the checkbox is for.
3. When the draft is ready, it appears as an internal note with its
   confidence level. Press **Review AI draft** and choose:
   - *Approved as is*: the reply is sent as it is;
   - *Modified*: correct the text and select a reason;
   - *Rejected*: select a reason; nothing is sent to the customer.

   Changing the text of a draft marked as approved counts as modified and
   requires a reason. The reasons *Other* and *Personal data slipped
   through* require a note. Any placeholder left in the reply (`[PERSON_1]`,
   known or not) blocks the send: replace it with the real text by hand.

**Q&A archive**

1. In *AI Assistant / Configuration / Import Solved Tickets* choose period,
   teams, categories and whether to take the last staff reply or all of them.
   Tickets already in the archive are skipped.
2. In *AI Assistant / Q&A Archive* check each imported entry: correct the
   text if needed, set the usage (knowledge base or test set) and press
   **Validate**. Entries that may still contain personal data cannot be
   validated; editing a validated entry sends it back to validation.
3. Select the validated entries and run **Export the knowledge base for the
   AI (JSONL)** to update the RAG index. The test set has its own action and
   is never indexed.

**Metrics**

In *AI Assistant / Draft Log* the pivot view shows the outcomes by confidence
level: it checks that the level declared by the model is reliable.
