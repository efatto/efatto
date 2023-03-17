# Copyright 2016-2020 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Task and work in calendar event',
    'version': '12.0.1.0.3',
    'category': 'Extra Tools',
    'description':
        'Add task and project on calendar event',
    'author': 'Sergio Corato',
    'website': 'https://github.com/sergiocorato/efatto',
    'depends': [
        'project_timesheet_time_control',
        'calendar',
        'hr_timesheet',
        'project',
        'sale_timesheet',
    ],
    'data': [
        'views/event.xml',
    ],
    'installable': True,
}
