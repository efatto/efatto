# -*- coding: utf-8 -*-
#
#
#    Copyright (C) 2016 Sergio Corato - SimplERP srl (<http://www.simplerp.it>)
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
    'name': 'Hr timesheet task',
    'version': '8.0.0.0.0',
    'category': 'other',
    'author': 'Sergio Corato - SimplERP SRL',
    'description': 'This module add this functions:'
'- When create analytic timesheet from tasks, add task to analytic line; '
'- When create ',
    'website': 'http://www.simplerp.it',
    'license': 'AGPL-3',
    'depends': [
        'hr_timesheet_sheet',
        'project_timesheet',
        'project_task_fix_project_id',
    ],
    'conflicts':[
        'show_sequence_columns_easy_0',
    ],
    'data': [
        'views/hr_view.xml',
    ],
    'installable': True
}
