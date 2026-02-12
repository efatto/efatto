# Copyright 2026 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Product obsoloscence management",
    "version": "14.0.1.0.0",
    "author": "Sergio Corato",
    "website": "https://github.com/efatto/efatto",
    "category": "Tools",
    "license": "AGPL-3",
    "depends": [
        "product_state",
        # "product_state_active",
        "product_status",
        "purchase_stock",
    ],
    "summary": "Add crm lead for products, with reflex on stock "
    "warehouse orderpoint through Stock orderpoint generator sale module.",
    "data": [
        "data/ir_cron.xml",
        "views/product_state.xml",
        "views/product_product.xml",
    ],
    "installable": True,
}
