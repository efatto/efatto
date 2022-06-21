# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Stock move available date expected',
    'version': '12.0.1.0.4',
    'category': 'Stock',
    'description': """
    Add facility to view and change sale reserved on stock moves.
    """,
    'author': 'Sergio Corato',
    'website': 'https://efatto.it',
    'license': 'AGPL-3',
    'depends': [
        'mrp_sale_info',
        'purchase_line_procurement_group',
        'purchase_stock',
        'purchase_state_tag',
        'sale_mrp_link',
        'sale_stock',
        'stock_move_details',
        'stock_quant_manual_assign',
    ],
    'data': [
        'views/stock.xml',
        'views/sale.xml',
        'views/product.xml',
    ],
    'installable': True,
}
