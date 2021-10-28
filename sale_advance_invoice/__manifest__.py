# Copyright 2019-2020 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Sale advance invoice description from sale order lines',
    'version': '12.0.1.0.1',
    'category': 'other',
    'author': 'Sergio Corato',
    'description': 'Add ability to select order lines to print details in the'
                   'invoice',
    'website': 'https://efatto.it',
    'license': 'LGPL-3',
    'depends': [
        'sale',
    ],
    'data': [
        'views/sale.xml',
    ],
    'installable': True,
}
