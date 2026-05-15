# Copyright 2017 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Ricevute bancarie report with total by date",
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "author": "Sergio Corato",
    "website": "https://github.com/efatto/efatto",
    "summary": "Ricevute bancarie report with total by date",
    "license": "AGPL-3",
    "depends": [
        "l10n_it_riba_oca",
    ],
    "assets": {
        "web.report_assets_common": [
            "/l10n_it_ricevute_bancarie_total_report/static/src/css/report.scss",
        ],
    },
    "data": [
        "report/distinta_report.xml",
    ],
}
