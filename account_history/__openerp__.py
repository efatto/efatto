# -*- coding: utf-8 -*-
# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Account name history',
    'version': '8.0.1.0.1',
    'category': 'other',
    'author': 'Sergio Corato',
    'website': 'https://efatto.it',
    'license': 'AGPL-3',
    'description': 'Account name history data',
    'depends': [
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account.xml',
    ],
    'installable': True,
}
