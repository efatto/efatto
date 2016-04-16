# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Noviat nv/sa (www.noviat.com). All rights reserved.
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
    'name': 'Add XLS export to accounting reports',
    'version': '8.2.4.1',
    'license': 'AGPL-3',
    'author': 'Noviat',
    'category': 'Generic Modules/Accounting',
    'description': """

    This module adds XLS export to the following accounting reports:
        - horizontal report
    """,
    'depends': ['report_xls', 'account_financial_report_horizontal_ext'], #'account_financial_report_webkit',
    'data': [
        'wizard/horizontal_wizard_view.xml',
    ],
    'installable': True,
}
