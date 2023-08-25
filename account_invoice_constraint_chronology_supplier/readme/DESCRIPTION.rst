This module is a replacement of *account_invoice_constraint_chronology* to helps ensuring the chronology of customer and supplier invoice numbers, and excluding check on draft invoices.

It prevents the validation of invoices when:

* there are validated invoices with a later date in the same fiscal year
* supplier invoice have a date (which generates account move) prior of date_invoice in the same fiscal year

It differs from the original module because it ignores draft invoices with a prior date, include vendor invoices and check only the invoices on the same fiscal year.
