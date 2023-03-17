# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Account Invoice update purchase',
    'version': '12.0.1.0.0',
    'author': 'Sergio Corato',
    'website': 'https://github.com/sergiocorato/efatto',
    'license': 'AGPL-3',
    'category': 'Accounting',
    'depends': [
        'account_invoice_triple_discount',
        'product_cost_price_avco_sync',
        'purchase_batch_invoicing',
        'purchase_stock_price_unit_sync',
        'purchase_triple_discount',
    ],
    'data': [
        'security/security.xml',
        'views/account_view.xml',
    ],
    'installable': True,
}
