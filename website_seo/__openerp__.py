# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   
#################################################################################
{
    'name': 'Website SEO PRO',
    'category': 'Website',
    'sequence':1,
    'summary': 'Manage all SEO Information(Meta-tags, alt-tags on your images, etc) of all your products/categories in minutes !!!',
    'website': 'http://www.webkul.com',
    'version': '1.0',
    'description':"""
   ODOO SEO-PRO
===========================
    **Help and Support**
===========================
.. |icon_features| image:: website_seo/static/description/icon-features.png
.. |icon_support| image:: website_seo/static/description/icon-support.png
.. |icon_help| image:: website_seo/static/description/icon-help.png

|icon_help| `Help <https://webkul.com/ticket/open.php>`_ |icon_support| `Support <https://webkul.com/ticket/open.php>`_ |icon_features| `Request new Feature(s) <https://webkul.com/ticket/open.php>`_
    """,
    'author': 'Webkul Software Pvt. Ltd.',
    'depends': ['base','website_sale','website_webkul_addons','wk_wizard_messages'],
    'installable': True,
    'data': [
            'data/set_website_seo_config_defaults.xml',           
            'data/demo.xml',            
            'views/res_config_view.xml',   
            'views/template.xml',
            'views/website_seo.xml',
            'views/webkul_addons_config_inherit_view.xml',         
                  
    ],    
    'application': True,
    "auto_install": False,
    "images":['static/description/Banner.png'],
    "price": 59,
    "currency": 'EUR',
    
}