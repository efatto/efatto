# -*- coding: utf-8 -*-
#
#    Copyright (C) 2016 Sergio Corato - SimplERP srl (<http://www.simplerp.it>)
#    Copyright (c) 2015 Oihane Crucelaegui - AvanzOSC
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
    'name': 'Product label qr code',
    'version': '8.0.1.0.0',
    'category': 'Product Management',
    'description': "Make Product label QRCode and Data Matrix",
    'author': 'Sergio Corato - SimplERP Srl',
    'website': 'http://simplerp.it',
    'depends': [
        'report_aeroo',
        'report_branding',
    ],
    'external_dependencies': {
        'python': [
            'elaphe',
        ],
    },
    'data': [
        'report/reports.xml',
    ],
    'installable': True,
}
