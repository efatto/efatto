# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Stock action to unreserve',
    'version': '12.0.1.0.0',
    'category': 'other',
    'author': 'Sergio Corato',
    'description': 'Add stock action to unreserve - this module will be unuseful after '
                   'merge of PR on OCB.',
    'website': 'https://efatto.it',
    'depends': [
        'stock',
    ],
    'data': [
        'data/stock_data.xml',
    ],
    'installable': True,
}
