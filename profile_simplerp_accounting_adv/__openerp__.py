# -*- coding: utf-8 -*-
#
#
#    Copyright (C) 2016 Sergio Corato - SimplERP srl (<http://www.simplerp.it>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
{
    'name': 'Italy - SimplERP Srl profile Accounting Advanced',
    'version': '8.0.1.0.0',
    'category': 'other',
    'description': """
    Profilo applicazioni Contabilità Avanzata SimplERP
    """,
    'author': 'Sergio Corato - SimplERP SRL',
    'website': 'http://www.simplerp.it',
    'license': 'AGPL-3',
    "depends": [
        'account_fy_closing_template_7',
        'account_asset_management_percent',
        'account_cashflow',
        'account_move_report_xls',
        'l10n_it_invoice_intra_cee',
        'l10n_it_fatturapa_out',
        'l10n_it_ricevute_bancarie_data',
        'l10n_it_ricevute_bancarie_ext',
        'l10n_it_vat_registries_ext',
    ],
    "installable": True,
}
