# -*- coding: utf-8 -*-
# Copyright (C) 2019 Sergio Corato
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Project search by origin in sale order',
    'version': '10.0.1.0.2',
    'category': 'Extra Tools',
    'description':
        'Project search by origin in sale order. Origin is automatically '
        'get from sale order.',
    'author': 'Sergio Corato',
    'website': 'https://efatto.it',
    'license': 'LGPL-3',
    'depends': [
        'project',
        'sale_timesheet',
    ],
    'data': [
        'views/project.xml',
    ],
    'installable': False,
}
