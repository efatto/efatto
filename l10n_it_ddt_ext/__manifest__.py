#    Copyright (C) 2016-2019 Sergio Corato
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
{
    'name': 'DDT various fixes',
    'version': '11.0.1.0.0',
    'category': 'other',
    'author': 'Sergio Corato',
    'website': 'https://efatto.it',
    'license': 'AGPL-3',
    'description': '''
This module add:
* ability to assign ddt type from sale order,
* ability to assign default create_ddt via company,
* fix use of fiscal sequence for ddt,
* limit domain to picking addable to ddt to not already in other ddts,
* remove package_id from tree view of ddts,
* add ddt start date,
* change ddt date type from datetime to date,
* check ddt number progression on date last ddt emitted on the same sequence
and fix date when not right,
* fill ddt data from ddt type when not filled in sale order of partner,
* block cancel of sale order is ddt and picking linked are in states done or 
in pack.''',
    'depends': [
        'stock_picking_package_preparation',
        'l10n_it_ddt',
    ],
    'data': [
        'views/sale.xml',
        'views/stock.xml',
        'views/config.xml',
    ],
    'installable': True,
    'auto-install': False,
    'application': False,
}
