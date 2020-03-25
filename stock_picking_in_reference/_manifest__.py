# Copyright 2017-2020 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Stock picking in reference',
    'version': '12.0.1.0.0',
    'category': 'other',
    'author': 'Sergio Corato',
    'website': 'http://www.efatto.it',
    'license': 'AGPL-3',
    'description': """
    Add reference of in document in stock picking.
    """,
    'depends': [
        'stock',
        'stock_picking_invoice_link',
    ],
    'data': [
        'views/picking_view.xml',
        'views/invoice.xml',
    ],
    'installable': True
}
