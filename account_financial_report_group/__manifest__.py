# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Financial report partner group",
    "summary": "Add financial report group methods for partner",
    "version": "12.0.1.0.0",
    "category": "Accounting & Finance",
    "website": "https://github.com/sergiocorato/efatto",
    "author": "Sergio Corato",
    "maintainers": ["sergiocorato"],
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "account_financial_report",
    ],
    "data": [
        'wizard/general_ledger_wizard_view.xml',
        'report/general_ledger.xml',
    ],
    "auto_install": False,
}
