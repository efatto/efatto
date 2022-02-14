# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': "Force DDT Number",
    'version': '12.0.1.0.0',
    'category': 'Stock',
    'summary': "Allows to force number on specific DN",
    'description': """
This module allows to force the ddt numbering.
It make visible the ddt_number field. If user fills that field, the typed
value will be used as ddt number.
Otherwise, the next sequence number will be retrieved and saved.
So, the new field has to be used when user doesn't want to use the default
ddt numbering for a specific ddt.
    """,
    'author': "Sergio Corato",
    'website': 'http://www.efatto.it',
    'license': 'AGPL-3',
    'depends': [
        'l10n_it_delivery_note',
    ],
    'data': [
        'wizard/delivery_note_create.xml',
    ],
    'installable': True,
}
