# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Purchase supplierinfo update',
    'version': '12.0.1.0.1',
    'category': 'Extra Tools',
    'description':
        'Update supplierinfo on purchase approve - before purchase order creation',
    'author': 'Sergio Corato',
    'website': 'https://efatto.it',
    'license': 'LGPL-3',
    'depends': [
        'purchase_order_approved',
    ],
    'data': [
        'views/supplierinfo.xml',
    ],
    'installable': True,
}
