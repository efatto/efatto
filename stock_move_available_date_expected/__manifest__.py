# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Stock move reserved sale',
    'version': '12.0.1.0.2',
    'category': 'Stock',
    'description': """
    Add facility to view and change sale reserved on stock moves.
    """,
    'author': 'Sergio Corato',
    'website': 'https://www.efatto.it',
    'license': 'AGPL-3',
    'depends': [
        'mrp',
        'purchase_stock',
        'sale_stock',
        'stock_quant_manual_assign',
        'stock',
    ],
    'data': [
        'views/stock.xml',
        'views/sale.xml',
    ],
    'installable': True,
}
