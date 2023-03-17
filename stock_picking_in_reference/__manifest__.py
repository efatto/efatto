# Copyright 2017-2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'IN DDT reference',
    'version': '12.0.1.0.1',
    'category': 'other',
    'author': 'Sergio Corato',
    'website': 'https://github.com/sergiocorato/efatto',
    'description': """
    Show reference of incoming DDT in supplier invoice in tree view and in picking.
    """,
    'depends': [
        'stock',
        'stock_picking_invoice_link',
        'l10n_it_ddt',
    ],
    'data': [
        'views/picking_view.xml',
        'views/invoice.xml',
    ],
    'installable': True
}
