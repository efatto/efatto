# Copyright 2019-2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Account analytic project',
    'version': '12.0.1.0.2',
    'category': 'Extra Tools',
    'description':
        'Account analytic project',
    'author': 'Sergio Corato',
    'website': 'https://efatto.it',
    'depends': [
        'analytic',
        'analytic_show_invoice',
        'analytic_show_sale',
        'hr_timesheet',
        'project',
    ],
    'data': [
        'views/account.xml',
        'views/project.xml',
    ],
    'installable': True,
}
