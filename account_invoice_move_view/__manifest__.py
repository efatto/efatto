# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Stock move with lots in invoice line form',
    'version': '12.0.1.0.0',
    'category': 'other',
    'description': """
    Stock move and lots visibile in invoice line form
    """,
    'author': 'Sergio Corato',
    'website': 'https://www.efatto.it',
    'license': 'AGPL-3',
    'depends': [
        'purchase_stock',
    ],
    'data': [
        'views/account_invoice.xml',
    ],
    'installable': True,
}
