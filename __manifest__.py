# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Sale stock mrp produce delay",
    "version": "12.0.1.0.2",
    "category": "other",
    "author": "Sergio Corato - Efatto.it",
    "website": "https://efatto.it",
    "description": """
    Improvements:
    1. add produce_delay and purchase_delay (delay for purchase from the first sellers)
       to customer lead date to compute scheduled date,
    2. do not set scheduled date equal to commitment date,
    3. set icon of stock info red accordingly.""",
    "depends": [
        "mrp",
        "purchase_stock",
        "sale_order_line_date",
        "sale_stock_info_popup",
    ],
    "data": [
        "views/product.xml",
    ],
    "qweb": [
        "static/src/xml/qty_at_date.xml",
    ],
    "installable": True
}
