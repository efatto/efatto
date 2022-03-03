# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Stock rule dropship partner',
    'version': '12.0.1.0.0',
    'category': 'other',
    'author': 'Sergio Corato',
    'description': 'Add partner for stock picking created by dropship.',
    'website': 'https://efatto.it',
    'depends': [
        'stock',
    ],
    'data': [
        'views/stock_rule.xml',
    ],
    'installable': True,
}
