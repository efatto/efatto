# -*- coding: utf-8 -*-
# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Stock move analytic on delivery',
    'version': '8.0.1.0.0',
    'category': 'other',
    'author': 'Sergio Corato',
    'website': 'https://efatto.it',
    'license': 'AGPL-3',
    'description': 'Create analytic lines on delivery',
    'depends': [
        'stock_analytic',
    ],
    'data': [
        'data/stock.xml',
        'views/stock.xml',
    ],
    'installable': True,
}
