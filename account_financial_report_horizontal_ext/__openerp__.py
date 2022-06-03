# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2012 Therp BV (<http://therp.nl>),
#    Copyright (C) 2013 Agile Business Group sagl
#    (<http://www.agilebg.com>) (<lorenzo.battistini@agilebg.com>)
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
    "name": "Accounting Financial Reports Horizontal Ext",
    "version": "8.0.1.13.9",
    "author": ["Therp BV", "Agile Business Group", "Didotech srl", "Sergio Corato"],
    "category": 'Accounting & Finance',
    'complexity': "normal",
    "description": """
This is a port to OpenERP 8.0 of the horizontal financial reports
'Balance sheet' and 'Profit and Loss' as found in OpenERP 7.0.
    """,
    'website': 'https://www.efatto.it',
    "depends": [
        'account',
    ],
    'data': [
        'menu.xml',
        'account_report.xml',
        'wizard/account_report_common_view.xml',
        'wizard/account_report_balance_sheet_view.xml',
        'wizard/account_report_profit_loss_view.xml',
    ],
    'installable': True,
    'active': False,
}
