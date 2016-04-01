# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Ditron Hardware Driver',
    'version': '8.0.0.1.0',
    'category': 'Hardware Drivers',
    'summary': 'Hardware Driver for Italian Fiscal Ditron',
    'website': 'https://www.simplerp.it',
    'author': 'Sergio Corato - SimplERP Srl',
    'description': 'Hardware Driver for Italian Fiscal Ditron',
    'depends': [
        'point_of_sale',
        'hw_proxy',
    ],
    'qweb': ['static/src/xml/pos.xml'],
    'installable': True,
    'auto_install': False,
}
