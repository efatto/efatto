# -*- coding: utf-8 -*-
# Copyright 2016-2019 Sergio Corato
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account invoice check VAT statement",
    "version": "10.0.1.0.3",
    "category": "Accounting",
    "description": """
Check if exists a closed VAT statement for period used to register the invoice:
if true, raise an error.
""",
    "author": "Sergio Corato",
    "website": "https://efatto.it",
    "license": "AGPL-3",
    "depends": [
        "account",
        "account_vat_period_end_statement",
    ],
    "installable": True
}
