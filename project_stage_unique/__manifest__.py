# Copyright 2016-2020 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Project task type name unique',
    'version': '12.0.1.0.0',
    'category': 'Extra Tools',
    'description':
        'With this module the task type name does not accept duplicates.',
    'author': 'Sergio Corato',
    'website': 'https://efatto.it',
    'license': 'LGPL-3',
    'depends': [
        'project_task_default_stage',
    ],
    'data': [
    ],
    'installable': True,
    'pre_init_hook': 'pre_init_hook',
}
