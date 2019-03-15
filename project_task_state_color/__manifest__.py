# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2018 Sergio Corato
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
    'name': 'Project task colors',
    'version': '10.0.1.0.0',
    'category': 'Extra Tools',
    'description':
        'Change task color on state.',
    'author': 'Sergio Corato',
    'website': 'https://efatto.it',
    'depends': [
        'calendar',
        'project',
        'project_task_partner_shipping',
        'web_widget_color',
    ],
    'data': [
        'views/project.xml',
        'views/calendar.xml',
    ],
    'installable': False,
}
