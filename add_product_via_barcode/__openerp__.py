# -*- coding: utf-8 -*-
{
    'name': "Add Products By Barcode",

    'summary': """
        Add products to sale and purchase order by barcode and internal reference.""",

    'description': """
       Add products to sale and purchase order by barcode and internal reference.
    """,

    'author': "DRC Systems India Pvt. Ltd.",
    'website': "http://www.drcsystems.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sale',
    'version': '0.1',
    'depends': [
        'sale', 'purchase'],
    'data': [
        'views/templates.xml',
    ],

    'images': ['static/description/barcode-scanner.jpg'],
    'installable': True,
}
