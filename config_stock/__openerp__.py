# -*- coding: utf-8 -*-
#
#
#    Copyright (C) 2016-2018 Sergio Corato
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
    'name': 'Module to configure stock',
    'version': '9.0.1.0.0',
    'category': 'other',
    'description': """
Module to configure stock.
Add the next groups to base user:
- inventory valuation;
- stock packaging;
- locations. NO MORE EXISTS
It also set invoice policy default to delivery.
""",
    'author': 'Sergio Corato',
    'website': 'https://efatto.it',
    'license': 'AGPL-3',
    "depends": [
        'sale',
        'stock_account',
    ],
    "data": [
        'data/group.xml',
    ],
    'installable': True
}
