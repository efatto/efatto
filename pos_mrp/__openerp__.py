# -*- coding: utf-8 -*-
#
#
#    Copyright (C) 2016 SimplERP srl (<http://www.simplerp.it>).
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
    'name': 'Pos create MRP procurement',
    'version': '8.0.0.0.0',
    'category': 'Hidden',
    'description': "Pos create MRP procurement",
    'author': 'Sergio Corato - SimplERP Srl',
    'website': 'http://simplerp.it',
    'depends': ['mrp', 'point_of_sale', 'sale'],
    'data': [
        'data/pos_mrp_data.xml',
        'views/pos_mrp_view.xml',
    ],
    'installable': True,
}

