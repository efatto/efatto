# Copyright 2026 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Product status with replacement",
    "version": "14.0.1.0.0",
    "author": "Sergio Corato",
    "website": "https://github.com/efatto/efatto",
    "category": "Tools",
    "license": "AGPL-3",
    "depends": [
        "product_state",
        "product_status",
        "purchase_stock",
    ],
    "data": [
        "data/ir_cron.xml",
        "views/product_product.xml",
    ],
    "installable": True,
}
