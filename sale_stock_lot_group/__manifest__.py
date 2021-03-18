# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Sale stock lot group',
    'version': '12.0.1.0.0',
    'category': 'Extra Tools',
    'description':
        'Add group to sale button in stock lot',
    'author': 'Sergio Corato',
    'website': 'https://efatto.it',
    'depends': [
        'sale_stock',
    ],
    'data': [
        'views/sale.xml',
    ],
    'installable': True,
}
