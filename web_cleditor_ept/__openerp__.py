{
    'name': 'Web Cleditor Extension',
    'summary' : 'Enable full list of options in Cleditor',
    'category': 'web',  # 'Social Network',
    'author':'Emipro Technologies Pvt. Ltd.',
    'version': '1.0',
    'website': 'www.emiprotechnologies.com',
    'description':
        """
After installing this module user will able to see full list of options in Cleditor

Contact : info@emiprotechnologies.com for any kind of services on Odoo V8.
        """,
    'data': ['views/web_cleditor_ept.xml', ],
    'depends': ['web'],
    'images': ['static/description/main_screen.png'],
    'installable': True,
    'auto_install': False,
    'application': True,
    'qweb' : [],

}

