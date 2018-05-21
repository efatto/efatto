# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (C) 2015-2017 Sergio Corato
#    Copyright (C) 2014 Didotech srl
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
    "name": 'Account chart autoconfigurable',
    "version": "8.0.0.2.2",
    "depends": [
        'base_vat',
        'account',
        'l10n_it_account',
    ],
    "author": "Sergio Corato",
    "description": """
    Autoconfigure tax pdc during installation.
    This module is useful only is installed with a configured chart.
    """,
    "license": "AGPL-3",
    "category": "Localisation/Italy",
    'website': 'http://www.efatto.it',
    'data': [
        'data/account_tax_view.xml',
        'data/payment_type_view.xml',
    ],
    'installable': False,
}
