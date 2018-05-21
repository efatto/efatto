# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016-2017 Sergio Corato
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
    'name': 'Task and work in calendar event',
    'version': '8.0.1.0.0',
    'category': 'Extra Tools',
    'description':
        'Manage task and work from calendar event',
    'author': 'Sergio Corato',
    'website': 'http://www.efatto.it',
    'depends': [
        'calendar',
        'hr_timesheet',
        'hr_timesheet_tree_task',
        'project',
        'project_stage_state',
    ],
    'data': [
        'views/event.xml',
    ],
    'installable': False,
}
