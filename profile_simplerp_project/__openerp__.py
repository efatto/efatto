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
    'name': 'Italy - SimplERP Srl profile project apps',
    'version': '8.0.0.0.0',
    'category': 'other',
    'description': """
    Profilo applicazioni SimplERP hr & project
    """,
    'author': 'Sergio Corato - SimplERP SRL',
    'website': 'http://www.simplerp.it',
    'license': 'AGPL-3',
    "depends": [
        'hr_timesheet_sheet',
        'hr_timesheet_invoice',
        'gantt_improvement_ext',
        'project',
        'project_extenssion',
        'project_timesheet',
        'project_task_materials_stock_ext',
        'project_task_recalculate',
        'project_task_repetition',
        'project_task_work_print',
        'reminder_task_deadline',
    ],
    "installable": True,
}
