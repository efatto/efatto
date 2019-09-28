# -*- coding: utf-8 -*-
# Copyright 2019 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Account analytic SAL',
    'version': '10.0.1.0.34',
    'category': 'Extra Tools',
    'description':
        'Account analytic SAL',
    'author': 'Sergio Corato',
    'website': 'https://efatto.it',
    'depends': [
        'analytic',
        'contract_show_invoice',
        'contract_show_sale',
        'hr_timesheet',
        'project',
        'contacts',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account.xml',
        'views/project.xml',
        'views/sale.xml',
    ],
    'installable': True,
}
