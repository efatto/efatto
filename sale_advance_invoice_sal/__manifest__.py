# Copyright 2017-2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Sale advance invoice extension with SAL',
    'version': '12.0.1.0.2',
    'category': 'other',
    'author': 'Sergio Corato',
    'description': 'Add ability to get description from SAL of contract during '
                   'advance invoice creation. Link to SAL on analytic account.',
    'website': 'https://efatto.it',
    'license': 'AGPL-3',
    'depends': [
        'sale_advance_invoice',
        'account_analytic_sal',
    ],
    'data': [
        'views/sale.xml',
    ],
    'installable': True
}
