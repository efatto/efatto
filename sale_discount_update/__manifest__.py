# Copyright 2016-2020 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Update discount in sale order',
    'version': '12.0.1.0.0',
    'category': 'Sale Management',
    'license': 'LGPL-3',
    'description': """
    Add the ability to update discount in all sale order lines with a button.
    """,
    'author': "Sergio Corato",
    'depends': [
        'sale',
    ],
    'data': [
        'views/sale.xml'
    ],
    'installable': True,
}
