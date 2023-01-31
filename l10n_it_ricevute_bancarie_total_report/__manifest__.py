# Copyright 2017-2023 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Ricevute bancarie report with total by date',
    'version': '12.0.1.0.1',
    'category': 'Accounting',
    'author': 'Sergio Corato',
    'website': 'https://efatto.it',
    'description': 'Ricevute bancarie report with total by date',
    'license': 'AGPL-3',
    'depends': [
        'l10n_it_ricevute_bancarie',
    ],
    'data': [
        'report/report_view.xml',
        'report/distinta_report.xml',
    ],
}
