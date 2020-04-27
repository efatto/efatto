# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Stock picking force assign',
    'version': '12.0.1.0.0',
    'category': 'other',
    'author': 'Sergio Corato',
    'website': 'https://efatto.it',
    'license': 'LGPL-3',
    'description': '''
This module add a button to force assign of stock moves with manual inserted 
completed quantity, available only to user with force stock picking group.''',
    'depends': [
        'stock',
    ],
    'data': [
        'security/security.xml',
        'views/stock.xml',
    ],
    'installable': True,
}
