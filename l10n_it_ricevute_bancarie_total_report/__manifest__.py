# Copyright 2017-2020 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Ricevute bancarie report with total by date',
    'version': '12.0.1.0.0',
    'category': 'Accounting',
    'author': 'Sergio Corato',
    'website': 'https://efatto.it',
    'description': 'Ricevute bancarie report with total by date',
    'license': 'LGPL-3',
    'depends': [
        'l10n_it_ricevute_bancarie',
    ],
    'data': [
        'report/report_view.xml',
        'report/distinta_report.xml',
    ],
}
