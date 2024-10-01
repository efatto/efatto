# Copyright 2024 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Openupgrader",
    "version": "14.0.1.0.0",
    "category": "Odoo Management",
    "author": "Sergio Corato",
    "license": "AGPL-3",
    "summary": "Migrate Odoo.",
    "website": "https://github.com/sergiocorato/efatto",
    "depends": [
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/openupgrader_view.xml",
    ],
    "installable": True,
}
