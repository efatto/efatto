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
    'name': 'Italy - SimplERP Srl profile',
    'version': '4.0.0.0',
    'category': 'other',
    'description': """
    Profilatura SimplERP
    """,
    'author': 'SimplERP SRL',
    'website': 'http://www.simplerp.it',
    'license': 'AGPL-3',
    "depends": [
        'base_setup',
        'base_iban',
        'sale',
        'account',
        'account_invoice_entry_date',
        'account_invoice_merge',
        'account_auto_fy_sequence',
        'account_cancel',
        'account_withholding_tax',
        'l10n_it_invoice_intra_cee',
        'l10n_it_base',
        'l10n_it_base_location_geonames_import',
        'l10n_it_fiscalcode',
        'l10n_it_abicab',
        'l10n_it_pec',
        'l10n_it_vat_registries',
        'account_vat_period_end_statement',
    ],
    "data": [
    ],
    "demo": [],
    "active": False,
    "installable": True,
}
