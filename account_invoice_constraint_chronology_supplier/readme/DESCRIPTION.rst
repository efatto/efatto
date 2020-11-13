This module is a replacement of *account_invoice_constraint_chronology* to helps ensuring the chronology of supplier invoice numbers, and
 excluding check on draft invoices.

It prevents the validation of invoices when:

~* there are draft invoices with a prior date~
* there are validated invoices with a later date
* supplier invoice have a date (which generates account move) prior of date_invoice
