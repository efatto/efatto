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
    'name': 'DDT template and fiscal sequence',
    'version': '8.1.0.0.0',
    'category': 'other',
    'author': 'Sergio Corato - SimplERP SRL',
    'website': 'http://www.simplerp.it',
    'license': 'AGPL-3',
    'description': '''This module add:
    - possibility to create template ddt,
    - assign via company if create_ddt is default,
    - use of fiscal sequence for ddt.''',
    'depends': [
        'l10n_it_ddt',
    ],
    'data': [
        'views/sale.xml',
        'views/stock.xml',
        'views/config.xml',
    ],
    'installable': True
}
