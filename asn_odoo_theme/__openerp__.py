{
    'name': 'Odoo 9 Backend-Theme',
    'version': '1.0',
    'author': 'Ajeng Shilvie N',
    'description': '''
        A custom module to change menu bar like Odoo Enterprise
    ''',
    'category': 'Themes/ASN',
    'depends': [
        'base',
    ],
    'data': [
        'views/custom_view.xml',
    ],
    'css': ['static/src/css/styles.css'],
    'auto_install': False,
    'installable': True,
}
