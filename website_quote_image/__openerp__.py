# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################
{
    "name": "Website Quotation Images",
    "category": 'Website',
    "summary": """Add Product Images in website quotation.""",
    "description": """

====================
**Help and Support**
====================
.. |icon_features| image:: website_quote_image/static/src/img/icon-features.png
.. |icon_support| image:: website_quote_image/static/src/img/icon-support.png
.. |icon_help| image:: website_quote_image/static/src/img/icon-help.png

|icon_help| `Help <https://webkul.com/ticket/open.php>`_ |icon_support| `Support <https://webkul.com/ticket/open.php>`_ |icon_features| `Request new Feature(s) <https://webkul.com/ticket/open.php>`_
    """,
    "sequence": 1,
    "images":['static/description/Banner.png'],
    "author": "Webkul Software Pvt. Ltd.",
    "website": "http://www.webkul.com",
    "version": '8.0.0.2.0',
    "depends": ['base','website_quote'],
    "data": [
	'security/ir.model.access.csv',
        'views/website_quotation.xml',
        'report/sale_report.xml',
        ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "price": 15,
    "currency": 'EUR',
}