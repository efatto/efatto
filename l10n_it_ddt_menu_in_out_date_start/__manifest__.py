# Copyright 2016-2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'DDT supplier with date start glue module',
    'version': '12.0.1.0.0',
    'category': 'other',
    'author': 'Sergio Corato',
    'website': 'https://github.com/sergiocorato/efatto',
    'license': 'AGPL-3',
    'description': '''This auto-install module add date start in supplier DDT''',
    'depends': [
        'l10n_it_ddt_menu_in_out',
        'l10n_it_ddt_date_start',
    ],
    'data': [
        'views/stock.xml',
    ],
    'installable': True,
    'auto_install': True,
}
