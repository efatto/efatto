# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Stock reserve date check',
    'version': '12.0.1.0.0',
    'category': 'Stock Management',
    'author': 'Sergio Corato',
    'license': 'AGPL-3',
    'summary': 'Add logic to block confirmation of stock reservation on date not '
               'possible',
    'website': 'https://efatto.it',
    'depends': [
        'mrp_production_demo',
        'product_sellers_info',
        'sale_order_line_date',
        'sale_stock',
        'stock_move_available_date_expected',
    ],
    'data': [
        'views/mrp.xml',
        'views/sale.xml',
    ],
    'installable': True,
}
