# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
    'name': 'Manufacturing Order Merge and Split',
    'version': '1.0',
    'category': 'Manufacturing',
    'description': """
Merging and Spliting Manufacturing Order
========================================

This module allows you to merged multiple mo and split MO by creating multiple MO.

Main Features
-------------
* You can call wizard from list for merging operation with production list view.
* Splitting MO will be done from MO form view.for more detail you can refer following blog URL:
http://vperfectcs.com/blog/our-blogs-1/post/split-merge-manufacturing-orders-in-odoo-v8-0-10
    """,
    'author': 'VperfectCS',
    'website': 'http://www.vperfectcs.com',
    'depends': [
        'mrp_operations',
        'stock_account',
    ],
    'data': [
        'wizard/merge_mo_view.xml',
        'wizard/split_mo_view.xml',
        'mrp_production_view.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
