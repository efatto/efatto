# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################
{
    "name": "Website Webkul Addons",
    "category": 'Website',
    "summary": """
        Manage Webkul Website Addons""",
    "description": """

====================
**Help and Support**
====================
.. |icon_features| image:: website_webkul_addons/static/src/img/icon-features.png
.. |icon_support| image:: website_webkul_addons/static/src/img/icon-support.png
.. |icon_help| image:: website_webkul_addons/static/src/img/icon-help.png

|icon_help| `Help <https://webkul.com/ticket/open.php>`_ |icon_support| `Support <https://webkul.com/ticket/open.php>`_ |icon_features| `Request new Feature(s) <https://webkul.com/ticket/open.php>`_
    """,
    "author": "Webkul Software Pvt. Ltd.",
    "website": "http://www.webkul.com",
    "version": '8.0.1.0.0',
    "depends": ['base'],
    "data": [
        'views/webkul_addons_config_view.xml',
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
            "images":['static/description/Banner.png']
}