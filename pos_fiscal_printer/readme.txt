This module creates all that is necessary to print on a Fiscal Printer.

The solution is composed of 2 modules:
- pos_fiscal_printer - a core module
- pos_fp_<driver name> - driver module

Core module:
- disable printing from browser
- create configuration menu inside POS
- add departments
- load driver
- prepare all the data needed for creating a receipt

Driver module:
- compose a receipt
- sent receipt to printer

Menu Fiscal Printer gives you a possibility to match a Fiscal Printer
to a POS. Very often Fiscal Printers has only program for Windows,
which they call "Driver". This resident program expects to find a
receipt file in some directory. When it finds a new receipt it is
interpreted and send to a printer. We can't write to a file system
directly from JavaScript, so Client start printing and then Server
send a receipt to a computer which has fiscal printer attached.
Sometimes we also need to wright a password for the Fiscal Printer
inside receipt. This is the reason for 2 password fields.

Another type of printers accept printing via ethernet. Again we need
host/user/password.

An ECR (Electronic Cash Register) should register a
"department". Department depends on tax paid, so inside my Dummy
driver you will see:
reparto = line.product_id.taxes_id[0].department.department

Core module creates Department table, which should be compiled (in
Italy there are 3 main Departments: Reparto 1, Reparto 2, Reparto 3)
with corresponding numbers. These numbers are used to tell ECR to
which department a product belongs. After compiling the table, one
should go to Accounting / Configuration and select a right department
for the tax.

There is another option which can sound strange - "Dry Run". When we
print a receipt and something goes wrong, receipt will not disappear,
every time we try to print it will be send to a Fiscal Printer, so if
for any reason a receipt can't be printed it will block our POS until
the problem is resolved (a red ball appears in the right upper angle
of the POS). In this case one can select "Dry Run" option and when one
enters POS the queue will be emptied and a red ball became green. This
option can also be used if some receipts were printed directly from
ECR and one want to register this selling without reprinting a
receipt.
