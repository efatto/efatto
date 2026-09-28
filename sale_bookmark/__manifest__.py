# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale Bookmark",
    "version": "18.0.1.0.0",
    "author": "Sergio Corato",
    "website": "https://github.com/efatto/efatto",
    "category": "Tools",
    "license": "AGPL-3",
    "depends": [
        "product_is_kit",
        "sale",
        "stock",
    ],
    "summary": "",
    "data": [
        "data/ir_config_parameter.xml",
        "views/product.xml",
        "views/sale.xml",
    ],
    "installable": True,
    "post_init_hook": "post_init_hook",
}
