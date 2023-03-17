# Copyright 2020-2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Purchase supplierinfo on approved RFQ',
    'version': '12.0.1.1.0',
    'category': 'Extra Tools',
    'description':
        'Update supplierinfo on purchase approve - before purchase order creation',
    'author': 'Sergio Corato',
    'website': 'https://github.com/sergiocorato/efatto',
    'license': 'AGPL-3',
    'depends': [
        'purchase_discount',
        'purchase_order_approved',
    ],
    'data': [
    ],
    'installable': True,
}
