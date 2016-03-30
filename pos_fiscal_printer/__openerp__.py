# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2013-2014 Didotech srl (<http://www.didotech.com>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Fiscal Printer Management',
    'version': '8.0.0.3',
    'category': 'Point Of Sale',
    'description': """
    This module adds possibility to print a receipt on fiscal printer
    It prepares all values you may need when writing driver for your printer.
        
    """,
    'author': 'Andrei Levin',
    'depends': [
        'point_of_sale',
     ],
    'data': [
        'security/ir.model.access.csv',  # load access rights after groups
        'fiscal_printer_view.xml',
    ],
    'installable': True,
    'js': [
        'static/src/js/pos_fiscal_printer.js',
    ],
}

