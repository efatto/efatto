# -*- coding: utf-8 -*-
{
    'name': 'Demo Barcode Scanner',
    'version': '1.0',
    'category': '',
    "sequence": 14,
    'complexity': "easy",
    'category': 'Hidden',
    'description': """
        The current module is adding ability to select product with barcode scanner
        Barcode scanner is using built-in mobile phone camera and supports most of standard codes
        Scanner is added to product field in menu Warehouse -> Tracebility -> Stock Moves
        
    """,
    'author': 'Xpansa Group',
    'website': 'www.xpansa.com',
    'depends': ["base",'stock'],
    'init_xml': [],
    'data': [
        "views/stock_view.xml",
    ],
    'demo_xml': [],
    'test': [
    ],
    'qweb' : [
    ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
