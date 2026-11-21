**Draft replies**

1. Open a ticket and press **Prepare AI draft**. The *AI Assistant* tab shows
   the pseudonymized question.
2. Check the question. You can complete it with version, module and error
   message. Press **Approve and send the question**.
3. When the draft is ready, it appears as an internal note with its
   confidence level. Press **Review AI draft** and choose:
   - *Approved as is*: the reply is sent as it is;
   - *Modified*: correct the text and select a reason;
   - *Rejected*: select a reason; nothing is sent to the customer.

   Changing the text of a draft marked as approved counts as modified and
   requires a reason. The reasons *Other* and *Personal data slipped
   through* require a note.

**Q&A archive**

1. In *AI Assistant / Configuration / Import Solved Tickets* choose period,
   teams, categories and whether to take the last staff reply or all of them.
   Tickets already in the archive are skipped.
2. In *AI Assistant / Q&A Archive* check each imported entry: correct the
   text if needed, set the usage (knowledge base or test set) and press
   **Validate**. Entries that may still contain personal data cannot be
   validated.
3. Select the validated entries and run **Export for the AI (JSONL)** to
   update the RAG index.

**Metrics**

In *AI Assistant / Draft Log* the pivot view shows the outcomes by confidence
level: it checks that the level declared by the model is reliable.
