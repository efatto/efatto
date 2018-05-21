# -*- coding: utf-8 -*-

{
    'name': 'Update Product Cost from BOM',
    'version': '1',
    'category': 'Opencloud',
    'description': """ """,
    'author': 'Opencloud',
    'license': 'LGPL-3',
    'summary': 'Update product cost from Bill of Materials',
    'website': 'http://opencloud.pro',
    'depends': ['base','product','mrp'],
    'init_xml': [],
    'update_xml': [
        	"product_inherit_view.xml"
    ],
    'data': [],
    'css': [],
    'demo_xml': [],
    'qweb': ['static/src/xml/*.xml'],
    'test': [],
    'installable': False,
    'application': False,
    'auto_install': False,
    'images': ['images/imagem_upd_prod.png'],
    'price': 39.00,
    'currency': 'EUR',
}
