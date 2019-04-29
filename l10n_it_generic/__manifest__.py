# -*- coding: utf-8 -*-
#
#
#    Copyright (C) 2015-2018 Sergio Corato
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
    'name': 'Italy - PDC 7 number generic',
    'version': '10.0.1.1.0',
    'category': 'Localization/Account Charts',
    'description': """
    Italy PDC with 7 number generic
    """,
    'author': 'Sergio Corato',
    'website': 'https://efatto.it',
    'license': 'AGPL-3',
    "depends": [
        'account',
        'base_vat',
        'base_iban',
    ],
    "data": [
        'data/account_chart.xml',
        'data/data_account_type.xml',
        'data/account.account.template.csv',
        'data/account.tax.group.csv',
        'data/account.tax.template.csv',
        'data/account.fiscal.position.template.csv',
        'data/account.fiscal.position.tax.template.csv',
        'data/account.chart.template.csv',
        'data/account_chart_template_data.yml',
    ],
    "installable": True,
}
