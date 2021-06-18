# Copyright 2016-2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Italian central journal subtotal',
    'version': '12.0.1.0.0',
    'category': 'other',
    'author': 'Sergio Corato',
    'description': 'Add subtotal to page in central journal report',
    'website': 'https://efatto.it',
    'license': 'AGPL-3',
    'depends': [
        'l10n_it_account',
        'l10n_it_central_journal',
    ],
    'data': [
        'report/report_account_central_journal.xml',
        'wizard/print_giornale.xml',
    ],
    'installable': True
}
