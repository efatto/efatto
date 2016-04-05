# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'POS Fiscal',
    'version': '8.0.0.2.0',
    'category': 'other',
    'summary': 'POS Fiscal',
    'website': 'https://www.simplerp.it',
    'author': 'Sergio Corato - SimplERP Srl',
    'description': 'POS Fiscal',
    'depends': [
        'point_of_sale',
        # 'account_tax_department', unimplemented in js
    ],
    'data': [
        'views/point_of_sale.xml',
    ],
    'qweb': ['static/src/xml/pos.xml'],
    'installable': True,
}
