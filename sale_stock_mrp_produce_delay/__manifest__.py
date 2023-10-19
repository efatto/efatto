# Copyright 2021-2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale stock mrp produce delay",
    "version": "14.0.1.0.0",
    "category": "other",
    "author": "Sergio Corato",
    "website": "https://github.com/sergiocorato/efatto",
    "license": "AGPL-3",
    "depends": [
        "mrp_production_demo",
        "product_sellers_info",
        "sale_backorder",
        "sale_order_archive",
        "sale_order_line_date",
        "stock_move_available_date_expected",
    ],
    "data": [
        "views/product_view.xml",
        "views/sale_order_view.xml",
    ],
    "qweb": [
        "static/src/xml/qty_at_date.xml",
    ],
    "installable": True,
}
