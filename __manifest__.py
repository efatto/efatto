# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Sale stock mrp produce delay",
    "version": "12.0.1.0.0",
    "category": "other",
    "author": "Sergio Corato - Efatto.it",
    "website": "https://efatto.it",
    "description": """
    Two improvements:
    1. add produce_delay to customer lead date to compute scheduled date,
    2. do not set scheduled date equal to commitment date,""",
    "depends": [
        "mrp",
        "sale_stock_info_popup",
    ],
    "data": [
    ],
    "installable": True
}
