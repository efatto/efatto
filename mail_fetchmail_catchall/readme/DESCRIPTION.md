Incoming emails fetched by a *Fetchmail Server* are routed through the mail
aliases. When no alias matches the recipients, Odoo raises an error and the
fetchmail server discards the email. The standard *Create a New Record* field
(``object_id``) is the only fallback: if it is empty, the email is lost.

This module makes that fallback behaviour complete:

* when *Create a New Record* is set, it is used only for the emails that no
  alias and no reply can route, i.e. exactly the emails that would otherwise be
  discarded;
* when *Create a New Record* is empty, the same emails are stored in a
  lightweight *Catch-all Mail* inbox instead of being lost;
* emails written directly to the configured catch-all address are stored too,
  instead of being bounced.

The full email body and its attachments remain available in the catch-all
record's chatter.

Migration note
==============

In 14.0 the fetchmail server's ``object_id`` is a technical link to the
``ir.model`` row of the selected model. The link is a foreign key with
``ON DELETE SET NULL``: if that model is removed (not simply renamed) by 18.0,
the migration clears ``object_id`` and the fetchmail server would drop
unroutable emails. This module catches them in *Catch-all Mail* instead.
