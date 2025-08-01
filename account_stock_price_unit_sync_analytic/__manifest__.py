# Copyright 2023 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Account stock analytic price unit sync',
    'summary': 'Update cost price in the same analytic account stock moves already '
               'done',
    'version': '12.0.1.0.0',
    'category': 'Accounting',
    'author': 'Sergio Corato',
    'website': 'https://github.com/efatto/efatto',
    'license': 'AGPL-3',
    'installable': True,
    'depends': [
        'account',
        'account_analytic_mrp_extra_cost',  # depend on this only to exclude_extra_cost field  # noqa
        'mrp_production_procurement_analytic',
        'sale_mrp',
    ],
    'data': [
        'views/account_view.xml',
        'views/stock_move.xml',
    ],
}
