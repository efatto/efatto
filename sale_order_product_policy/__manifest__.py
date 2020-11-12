# Copyright 2019-2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Sale order product policy',
    'version': '12.0.1.0.0',
    'category': 'Extra Tools',
    'description':
        'Show product invoice policy in sale order line',
    'author': 'Sergio Corato',
    'website': 'https://efatto.it',
    'depends': [
        'sale',
    ],
    'data': [
        'views/sale.xml',
    ],
    'installable': True,
}
