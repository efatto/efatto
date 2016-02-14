# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 SimplERP srl (<http://www.simplerp.it>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Italy - Improved invoice report SimplERP',
    'version': '8.1.0.0.1',
    'category': 'other',
    'description': """
    Modifiche al report fattura
    """,
    'author': 'SimplERP SRL',
    'website': 'http://www.simplerp.it',
    'license': 'AGPL-3',
    "depends": [
        'report',
        'report_custom_filename',
        'sale',
        'account',
        'l10n_it_fiscalcode',
        'partner_subaccount',
    ],
    "data": [
        'views/report.paperformat_euro_invoice.xml',
        'views/invoice_css.xml',
        'views/account.report_invoice_document.xml',
        'views/account_invoice_report.xml',
    ],
    "installable": True,
}
