# Copyright 2018-2020 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Hide hr menu for not employed user',
    'version': '12.0.1.0.0',
    'category': 'other',
    'author': 'Sergio Corato',
    'description':
        'Hide hr menu (timesheet and holidays) for not employed user.',
    'website': 'https://efatto.it',
    'license': 'LGPL-3',
    'depends': [
        'hr',
        'hr_holidays',
        'hr_timesheet',
    ],
    'data': [
        'views/hr.xml',
    ],
    'installable': True,
}
