# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Purchase supplierinfo on approved RFQ',
    'version': '12.0.1.1.0',
    'category': 'Extra Tools',
    'description':
        'Update supplierinfo on purchase approve - before purchase order creation',
    'author': 'Sergio Corato',
    'website': 'https://efatto.it',
    'license': 'LGPL-3',
    'depends': [
        'purchase_discount',
        'purchase_order_approved',
    ],
    'data': [
    ],
    'installable': True,
}
