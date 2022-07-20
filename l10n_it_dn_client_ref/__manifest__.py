# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': "DN client order ref",
    'version': '12.0.1.0.0',
    'category': 'Stock',
    'summary': "Show client order ref on DN lines",
    'description': """
    Allows to use dropshipping with DN
    """,
    'author': "Sergio Corato",
    'website': 'https://efatto.it',
    'license': 'AGPL-3',
    'depends': [
        'l10n_it_delivery_note',
    ],
    'data': [
        'views/stock_delivery_note.xml',
    ],
    'installable': True,
}
