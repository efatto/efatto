# Copyright 2016-2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'DDT usability',
    'version': '12.0.1.0.1',
    'category': 'other',
    'author': 'Sergio Corato',
    'website': 'https://github.com/sergiocorato/efatto',
    'license': 'AGPL-3',
    'description': '''
This module add:
* show related pickings in sale order,
* fill ddt data from ddt type when not filled in sale order of partner,
* block cancel of sale order is ddt and picking linked are in states done or
in pack, else delete ddt updating last sequence number if the very last.''',
    'depends': [
        'stock_picking_package_preparation',
        'l10n_it_ddt',
    ],
    'data': [
        'views/sale.xml',
    ],
    'installable': True,
}
