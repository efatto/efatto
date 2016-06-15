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
    'name': 'POS Hotel',
    'version': '8.0.0.0.0',
    'category': 'other',
    'description': 'POS Hotel',
    'website': 'https://www.simplerp.it',
    'author': 'Sergio Corato - SimplERP Srl',
    'depends': [
        'point_of_sale',
        'hotel',
    ],
    'data': [
        'views/hotel_partner_view.xml',
        'views/point_of_sale.xml',
    ],
    'qweb': ['static/src/xml/pos.xml'],
    'installable': True,
}
