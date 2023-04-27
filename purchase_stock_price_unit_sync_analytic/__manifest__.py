# Copyright 2023 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Purchase stock analytic price unit sync',
    'summary': 'Update cost price in the same analytic account stock moves already '
               'done',
    'version': '12.0.1.0.0',
    'category': 'Purchase',
    'author': 'Sergio Corato',
    'website': 'https://github.com/sergiocorato/efatto',
    'license': 'AGPL-3',
    'installable': True,
    'depends': [
        'mrp_production_procurement_analytic',
        'purchase_stock_price_unit_sync',
        'sale_mrp',
    ],
}
