# Copyright 2016-2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'DDT date start and multi-year sequence ability',
    'version': '12.0.1.0.2',
    'category': 'other',
    'author': 'Sergio Corato',
    'website': 'https://github.com/sergiocorato/efatto',
    'license': 'AGPL-3',
    'description': '''
This module add:
* fix use of fiscal sequence for ddt,
* add ddt start date,
* change ddt date type from datetime to date,
* check ddt number progression on date last ddt emitted on the same sequence
and fix date when not right.''',
    'depends': [
        'stock_picking_package_preparation',
        'l10n_it_ddt',
    ],
    'data': [
        'views/stock.xml',
    ],
    'installable': True,
}
