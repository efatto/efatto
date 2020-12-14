# Copyright 2019-2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Project search by origin in sale order',
    'version': '12.0.1.0.0',
    'category': 'Extra Tools',
    'description':
        'Project search by origin in sale order. Origin is automatically '
        'get from sale order.',
    'author': 'Sergio Corato',
    'website': 'https://efatto.it',
    'license': 'AGPL-3',
    'depends': [
        'project',
        'sale_timesheet',
    ],
    'data': [
        'views/project.xml',
    ],
    'installable': True,
}
