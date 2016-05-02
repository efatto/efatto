# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 SimplERP SRL
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Italy - SimplERP Srl',
    'version': '8.0.0.0.1',
    'category': 'Localization/Account Charts',
    'description': """
    Profilatura SimplERP

    """,
    'author': 'SimplERP SRL',
    'website': 'http://www.simplerp.it',
    'license': 'AGPL-3',
    "depends": [
        'base_vat',
        'account_chart',
        'base_iban',
        'l10n_configurable',
        'partner_subaccount',
        'account_accountant',
        'account_payment_term_month',  # per il campo sequence e months
        #  'account_tax_simplified', da installare dopo perchè nel csv delle imposte non sono definiti i campi base_tax ecc.
    ],
    "data": [
        'data/payment_data.xml',
        'data/account.account.type.csv',
        'data/account.account.template.csv',
        'data/account.tax.code.template.csv',
        'data/account_chart.xml',
        'data/account.tax.template.csv',
        'data/account.fiscal.position.template.csv',
        'data/account.fiscal.position.tax.template.csv',
        'data/l10n_chart_it_generic.xml',
    ],
    "demo": [],
    "active": False,
    "installable": True,
}
