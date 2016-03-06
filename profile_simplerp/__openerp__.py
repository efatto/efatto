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
    'name': 'Italy - SimplERP Srl profile apps',
    'version': '8.0.0.0.0',
    'category': 'other',
    'description': """
    Profilo applicazioni SimplERP
    """,
    'author': 'Sergio Corato - SimplERP SRL',
    'website': 'http://www.simplerp.it',
    'license': 'AGPL-3',
    "depends": [
        'account_bank',
        'account_balance_line_view',
        'account_cancel',
        'account_due_list',
        'account_invoice_entry_date_ext',
        'account_invoice_force_number',
        'account_invoice_report_simplerp',
        'account_move_line_no_default_search',
        'account_move_line_report_xls',
        'base_setup',
        'base_iban',
        'contacts',
        'country_data_it',
        'disable_openerp_online',
        'l10n_it_abicab',
        'l10n_it_account_ext',
        'l10n_it_base_location_geonames_import',
        'l10n_it_fiscalcode',
        'l10n_it_pec',
        #'web_debranding',
    ],
    "installable": True,
}
