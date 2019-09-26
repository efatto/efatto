# Copyright 2019 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Module to configure sale',
    'version': '12.0.1.0.0',
    'category': 'other',
    'description': """
Module to configure sale.
Add the next groups to base user:
* sale.group_discount_per_so_line
* sale.group_delivery_invoice_address
* sale.group_warning_sale
* sale.group_sale_order_dates
Also set tax calculation rouding method as 'globally' and enable group sale
delivery address.
""",
    'author': 'Sergio Corato',
    'website': 'https://efatto.it',
    'license': 'LGPL-3',
    "depends": [
        'sale',
    ],
    "data": [
        'data/group.xml',
    ],
    'installable': True
}
