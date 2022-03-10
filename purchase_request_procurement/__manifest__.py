# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Purchase request procurement',
    'version': '12.0.1.0.0',
    'category': 'other',
    'author': 'Sergio Corato',
    'description': 'Add procurement to purchase request line.',
    'website': 'https://efatto.it',
    'depends': [
        'purchase_request',
        'sale_order_line_date',
    ],
    'data': [
        'views/purchase_request.xml',
    ],
    'installable': True,
}
