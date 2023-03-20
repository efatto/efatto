# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# Copyright 2019-2020 Sergio Corato <https://github.com/sergiocorato>

{
    'name': 'ITA - Reverse charge data',
    'version': '12.0.1.0.0',
    'category': 'Account',
    'description': 'Add default reverse charge data',
    'author': 'Sergio Corato',
    'website': 'https://github.com/sergiocorato/efatto',
    'license': 'AGPL-3',
    'depends': [
        'l10n_it_reverse_charge',
    ],
    'data': [
        'data/account_data.xml',
    ],
    'installable': True,
}
