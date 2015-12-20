# -*- coding: utf-8 -*-
#
#
#    Copyright (C) 2015 SimplERP srl (<http://www.simplerp.it>).
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
    'name': 'Account smart reporting',
    'version': '8.0.0.0.0',
    'category': 'other',
    'author': 'SimplERP SRL',
    'website': 'http://www.simplerp.it',
    'license': 'AGPL-3',
    'depends': [
        'account',
        'report',
    ],
    'data': [
        'views/account_config_view.xml',
        'views/account_report.xml',
        'views/account_sales_report_mail.xml',
        #'views/hr_expense_report_mail.xml',
        'views/report.account_report_smart.xml',
    ],
    'installable': True
}
