# Copyright 2026 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Fetchmail Catch-all",
    "summary": "Store incoming emails that no alias can route in a simple "
    "catch-all inbox",
    "version": "18.0.1.0.0",
    "category": "Productivity/Discuss",
    "author": "Sergio Corato",
    "website": "https://github.com/efatto/efatto",
    "license": "AGPL-3",
    "depends": ["mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/mail_catchall_views.xml",
        "views/mail_catchall_menus.xml",
    ],
    "installable": True,
}
