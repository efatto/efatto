# Copyright 2016-2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Landscape general ledger report',
    'version': '12.0.1.0.0',
    'category': 'other',
    'author': 'Sergio Corato',
    'description': 'General report in a landscape layout',
    'website': 'https://efatto.it',
    'license': 'AGPL-3',
    'depends': [
        'account_financial_report',
    ],
    'data': [
        'report/reports.xml',
        'report/layouts.xml',
        'report/general_ledger.xml',
    ],
    'installable': True
}
