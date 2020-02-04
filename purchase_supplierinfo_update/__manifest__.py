# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Purchase supplierinfo update',
    'version': '12.0.1.0.0',
    'category': 'Extra Tools',
    'description':
        'Update supplierinfo on purchase approve - before purchase order creation',
    'author': 'Sergio Corato',
    'website': 'https://efatto.it',
    'depends': [
        'purchase',
        'purchase_order_approved',
    ],
    'installable': True,
}
