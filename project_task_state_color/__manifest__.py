# Copyright 2018-2020 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Project task colors',
    'version': '12.0.1.0.0',
    'category': 'Extra Tools',
    'description':
        'Change task color on state.',
    'author': 'Sergio Corato',
    'website': 'https://efatto.it',
    'license': 'LGPL-3',
    'depends': [
        'calendar',
        'project_stage_closed',
        'web_widget_color',
    ],
    'data': [
        'views/project.xml',
        'views/calendar.xml',
    ],
    'installable': True,
}
