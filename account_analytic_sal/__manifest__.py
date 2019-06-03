# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2017-2019 Sergio Corato
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Account analytic SAL',
    'version': '10.0.1.0.18',
    'category': 'Extra Tools',
    'description':
        'Account analytic SAL',
    'author': 'Sergio Corato',
    'website': 'https://efatto.it',
    'depends': [
        'analytic',
        'contract_show_invoice',
        'contract_show_sale',
        'project',
        'contacts',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account.xml',
        'views/project.xml',
    ],
    'installable': True,
}
