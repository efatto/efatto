# Copyright 2019-2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Account analytic line tag',
    'version': '12.0.1.0.0',
    'category': 'Extra Tools',
    'description':
        'Account analytic line tag',
    'author': 'Sergio Corato',
    'website': 'https://github.com/sergiocorato/efatto',
    'license': 'AGPL-3',
    'depends': [
        'analytic',
        'hr_timesheet',
        'project',
    ],
    'data': [
        'views/account.xml',
    ],
    'installable': True,
}
