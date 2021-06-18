# Copyright 2016-2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Italian central journal history',
    'version': '12.0.1.0.1',
    'category': 'Accounting & Finance',
    'author': 'Sergio Corato',
    'description': 'Italian Central Journal with history of partner',
    'website': 'https://efatto.it',
    'license': 'AGPL-3',
    'depends': [
        'l10n_it_central_journal_subtotal',
        'partner_history',
    ],
    'data': [
        'report/report_account_central_journal.xml',
    ],
    'installable': True,
    'auto_install': True,
}
