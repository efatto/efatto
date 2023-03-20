# Copyright 2018-2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Hide hr menu for not employed user',
    'version': '12.0.1.0.0',
    'category': 'other',
    'author': 'Sergio Corato',
    'description':
        'Hide hr menu (timesheet and holidays) for not employed user.',
    'website': 'https://github.com/sergiocorato/efatto',
    'license': 'AGPL-3',
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
