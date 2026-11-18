To configure the module, go to *Lost Mail \> Configuration*:

- *Settings*: choose the group notified when an email lands in the inbox
  and no rule handles it, whether to keep catch-all mail, whether to
  keep automatic and bulk mail, and the retention delays. The company of
  a lost email is taken from the mail alias domain of the recipient.
- *Routing Rules*: create rules matching the sender, the recipients or
  the subject. A rule can attach the email to the sender's contact,
  attach it to a fixed record, discard it or assign it to a user.
  Contact creation is off by default because the sender address comes
  from the email headers.

The incoming mail server must hand over the messages Odoo cannot route
(an incoming mail server or the mail gateway script, without a
restrictive *Create a New Record* model). The module acts when Odoo
finds no route; it does not read the mailbox by itself.
