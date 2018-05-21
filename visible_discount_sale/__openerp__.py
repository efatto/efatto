{
    'name': 'Visible Discount in Sale',
    'version': '1.0',
    'category': "Sales",
    'summary' : 'Enable discount visibility separately on Sale Order from pricelist',
    'description': """
        This module is used to set discount visiblity in sale order""",
    'author': 'Emipro Technologies Pvt. Ltd.',
    'website': 'http://emiprotechnologies.com',
    'depends': ['sale'],
    'data': [
                'security/sale_security_group.xml',
                'view/configuration_setting.xml',
                'view/product_pricelist_view.xml',
            ],
    'images': ['static/description/main_screen.png'],
    'installable': False,
    'auto_install': False,
    'application' : True,
    'price': 5.00,
    'currency': 'EUR',
}
