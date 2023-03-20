# Copyright 2019-2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Sale advance invoice description from sale order lines',
    'version': '12.0.1.0.1',
    'category': 'other',
    'author': 'Sergio Corato',
    'description': 'Add ability to select order lines to print details in the'
                   'invoice',
    'website': 'https://github.com/sergiocorato/efatto',
    'license': 'AGPL-3',
    'depends': [
        'sale',
    ],
    'data': [
        'views/sale.xml',
    ],
    'installable': True,
}
