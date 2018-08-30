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
    'name': 'Project task type name unique',
    'version': '9.0.1.0.0',
    'category': 'Extra Tools',
    'summary': 'Set project task type name (aka "stage") unique',
    'description':
        'With this module the task type name does not accept duplicates (case'
        ' insensitive). '
        'For better result, rename task with the same function but different '
        'name with the same name ("source" name) before installation.'
        'This module must be installed before createat db creation.',
    'author': 'Sergio Corato',
    'website': 'https://efatto.it',
    'depends': [
        'project_task_default_stage',
    ],
    'data': [
    ],
    'installable': True,
    'pre_init_hook': 'pre_init_hook',
}
