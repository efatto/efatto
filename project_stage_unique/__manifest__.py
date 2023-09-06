# Copyright 2016-2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Project task type name unique',
    'version': '12.0.1.0.0',
    'category': 'Extra Tools',
    'description':
        'With this module the task type name does not accept duplicates.',
    'author': 'Sergio Corato',
    'website': 'https://github.com/sergiocorato/efatto',
    'license': 'AGPL-3',
    'depends': [
        'project_task_default_stage',
    ],
    'data': [
    ],
    'installable': True,
    'pre_init_hook': 'pre_init_hook',
}
