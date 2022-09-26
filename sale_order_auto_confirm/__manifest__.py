# Copyright 2013 Creativiquadrati snc
# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Sale order auto confirm',
    'version': '12.0.1.0.1',
    'category': 'other',
    'author': 'Sergio Corato - Efatto.it',
    'website': 'https://efatto.it',
    'description': 'Sale order auto confirm',
    'license': 'AGPL-3',
    'depends': [
        'sale_order_calendar_state',
    ],
    'data': [
        'data/cron.xml',
    ],
    'installable': True
}
