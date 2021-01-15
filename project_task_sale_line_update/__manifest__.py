# Copyright 2019-2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Project task update sale',
    'version': '12.0.1.0.0',
    'category': 'Extra Tools',
    'description':
        'When updated sale line link in task, by default analytic line remain linked '
        'to the original sale line.',
    'author': 'Sergio Corato',
    'website': 'https://efatto.it',
    'depends': [
        'analytic',
        'sale',
        'hr_timesheet',
        'project',
    ],
    'data': [
    ],
    'installable': True,
}
