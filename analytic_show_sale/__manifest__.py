# -*- coding: utf-8 -*-
# Copyright (C) 2015 Angel Moya <angel.moya@domatix.com>
# Copyright (C) 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright (C) 2019-2020 Sergio Corato (https://efatto.it)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Analytic Show Sale',
    'summary': 'Button in analytic account to show its sales',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Sergio Corato',
    'website': 'https://github.com/sergiocorato/efatto',
    'depends': ['analytic', 'sale'],
    'category': 'Sales Management',
    'data': [
        'views/analytic_view.xml',
    ],
    'installable': True,
}
