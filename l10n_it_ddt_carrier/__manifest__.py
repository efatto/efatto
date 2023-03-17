# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Carrier in partner for DDT',
    'version': '12.0.1.0.0',
    'category': 'other',
    'author': 'Sergio Corato',
    'website': 'https://github.com/sergiocorato/efatto',
    'license': 'AGPL-3',
    'description': 'Add field to precompile carrier for DDT in partner.',
    'depends': [
        'l10n_it_ddt',
        'sale',
    ],
    'data': [
        'views/partner.xml',
    ],
    'installable': True,
}
