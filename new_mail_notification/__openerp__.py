# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2015-Today Vidhin Mehta (vidhin.mehta16@gmail.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################


{
    'name': 'New Mail Notification',
    'category': 'Tools',
    'description': """
Shows New Mail Notification in Sytem Tray.
==========================================
        """,
    'version': '8.0.1.0.0',
    'author': "Vidhin Mehta (vidhin.mehta16@gmail.com)",
    'depends':['web'],
    'data': ['views/notification.xml'],
    'qweb': ['static/src/xml/notification.xml'],
    'category': 'Tools',
    'auto_install': False,
}
