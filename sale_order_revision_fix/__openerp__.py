# -*- coding: utf-8 -*-
#
#    Copyright (C) 2018 Sergio Corato
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
    'name': "Sale order line revision fix",
    'version': '8.0.0.1.0',
    'category': 'Sale Management',
    'description': 'Fix order line state of old revision (actually they remain'
                   ' in "draft" state instead of "cancel".',
    'author': 'Sergio Corato - Efatto.it',
    'website': 'https://www.efatto.it',
    'license': 'AGPL-3',
    "depends": ['sale_order_revision'],
    "data": [
        ],
    "installable": True,
}
