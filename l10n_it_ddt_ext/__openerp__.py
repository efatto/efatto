# -*- coding: utf-8 -*-
#
#
#    Copyright (C) 2016-2017 Sergio Corato
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
    'version': '8.0.1.0.0',
    'category': 'other',
    'author': 'Sergio Corato',
    'website': 'http://www.efatto.it',
    'license': 'AGPL-3',
    'description': '''This module add:
    - possibility to create template ddt,
    - assign via company if create_ddt is default,
    - use of fiscal sequence for ddt.''',
    'depends': [
        'stock_picking_package_preparation',
        'l10n_it_ddt',
        'web_widget_digitized_signature',
        'report_aeroo_parser',
    ],
    'data': [
        'data/reports.xml',
        'views/sale.xml',
        'views/stock.xml',
        'views/config.xml',
    ],
    'installable': True
}
