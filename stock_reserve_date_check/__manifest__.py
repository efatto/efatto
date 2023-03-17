# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Stock reserve date check',
    'version': '12.0.1.0.0',
    'category': 'Stock Management',
    'author': 'Sergio Corato',
    'license': 'AGPL-3',
    'summary': 'Add logic to block confirmation of sale order on date not possible '
               'on product stock or predicted arrival and manufacturing time.',
    'website': 'https://github.com/sergiocorato/efatto',
    'depends': [
        'sale_stock_mrp_produce_delay',
    ],
    'data': [
        'views/sale.xml',
    ],
    'installable': True,
}
