# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Show RdP quantities in stock orderpoint",
    "version": "18.0.1.0.0",
    "category": "Stock Management",
    "author": "Sergio Corato",
    "summary": "Show quantities in draft and sent purchase order in stock orderpoint.",
    "website": "https://github.com/efatto/efatto",
    "license": "AGPL-3",
    "depends": [
        "purchase_stock",
        "mrp",
        "sale_management",
        "stock_orderpoint_manual_procurement",
    ],
    "data": [
        "views/stock.xml",
    ],
    "installable": True,
}
