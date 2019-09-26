# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016-2018 Sergio Corato
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
    'name': 'Project task date visible and coloured on kanban',
    'version': '10.0.1.0.1',
    'category': 'Extra Tools',
    'description':
        'With this module dates in kanban are more visible and coloured '
        'on stage basis.',
    'author': 'Sergio Corato',
    'website': 'https://efatto.it',
    'depends': [
        'project',
        'project_stage_state',
    ],
    'data': [
        'views/web_kanban.xml',
        'views/project_task_view.xml'
    ],
    'installable': False,
}
