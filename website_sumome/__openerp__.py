# (c) 2015 Ubiteck - Sébastien Ursini
#    'version': '8.0.1.0.0',
{
    'name': 'SumoMe - Website Traffic Tools',
    'version': '8.0.1.0.0',
    'author': 'Ubiteck - Sébastien Ursini',
    'category': 'Website',
    "summary": "SumoMe services for Odoo 8.0",
    'website': 'http://www.ubiteck.ch',
    'depends': ['website'],
    'data': [
        'views/website_config_settings.xml',
	'views/template.xml',
	'security/ir.model.access.csv',
    ],
    'images': [
              'static/description/sumome_banner.jpg',
    ],
    'installable': True,
    'auto_install': False,
    'price': '11.00',
    'currency': 'EUR',
}
