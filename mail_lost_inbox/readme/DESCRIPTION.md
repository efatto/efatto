Keep incoming emails that Odoo cannot route to any record: emails sent
to an unknown alias, a retired mailbox or (optionally) the catch-all
address.

Each email is stored in *Lost Mail \> Inbox* with its sender,
recipients, body, original headers and attachments. From the inbox a
user can attach the email to any record with a chatter, attach it to the
sender's contact (creating it if needed) or create a new record, without
copying the message. Automatic routing rules can also handle the email
as soon as it arrives.

Emails that Odoo can route itself (replies, known aliases, a configured
fallback model) are left untouched.
