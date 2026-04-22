# Copyright 2026 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Add a group for production lot creation",
    "version": "14.0.1.0.0",
    "category": "other",
    "author": "Sergio Corato",
    "summary": "Add a group for production lot creation",
    "website": "https://github.com/efatto/efatto",
    "license": "AGPL-3",
    "depends": [
        "mrp",
        "stock",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
}
