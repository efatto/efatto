# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Sale order info for components",
    "version": "14.0.1.0.0",
    "category": "other",
    "author": "Sergio Corato",
    "website": "https://github.com/sergiocorato/efatto",
    "summary": "Sale order info for product with components",
    "license": "AGPL-3",
    "depends": [
        "sale_bookmark",
        "sale_stock_mrp_produce_delay",
    ],
    "data": [
        "wizard/sale_order_component.xml",
        "views/sale.xml",
    ],
    "installable": True,
}
