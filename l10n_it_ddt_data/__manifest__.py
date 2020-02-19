# Copyright 2016-2020 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Italy - Default DDT data',
    'version': '12.0.1.0.0',
    'category': 'other',
    'description': '''
    Default datas for DDTs.
    ''',
    'author': 'Sergio Corato',
    'website': 'https://efatto.it',
    'license': 'AGPL-3',
    'depends': [
        'l10n_it_ddt',
    ],
    'data': [
        'data/ddt_type.xml',
        'data/stock_location.xml',
    ],
    'installable': True,
}
