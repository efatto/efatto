# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': "Force DDT Number",
    'version': '12.0.1.0.0',
    'category': 'Stock',
    'summary': "Allows to force number on specific DDT",
    'description': """
This module allows to force the ddt numbering.
It make visible the ddt_number field. If user fills that field, the typed
value will be used as ddt number.
Otherwise, the next sequence number will be retrieved and saved.
So, the new field has to be used when user doesn't want to use the default
ddt numbering for a specific ddt.
    """,
    'author': "Sergio Corato",
    'website': 'https://github.com/sergiocorato/efatto',
    'license': 'LGPL-3',
    'depends': [
        'l10n_it_ddt',
        'l10n_it_ddt_menu_in_out',
    ],
    'data': [
        'security/security.xml',
        'views/stock.xml'
    ],
    'installable': True,
}
