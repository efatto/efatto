# Copyright 2023 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Invoice analytic line mrp extra cost',
    'summary': 'Compute extra cost from analytic in invoices versus mrp stock moves',
    'version': '12.0.1.0.0',
    'category': 'Accounting',
    'author': 'Sergio Corato',
    'website': 'https://github.com/sergiocorato/efatto',
    'license': 'AGPL-3',
    'installable': True,
    'depends': [
        'account_group_invoice_line',
        'mrp_analytic',
    ],
    'data': [
        'views/account.xml',
    ],
}
