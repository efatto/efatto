# -*- coding: utf-8 -*-
{
    'name': 'Stocks Access Rules',
    'version': '1.1',
    'category': 'Warehouse',
    'summary': 'Restrict users access to stocks and locations',
    'description': '''
The app goal is to limit user access to a specified warehouse and location. The tool let you better control movements and organize geographically distributed warehouse system
*A user would see the stocks placed either on his/her locations or locations withouts accepted users stated
*Define users on the form of locations or locations on a the form of users. Both approaches would lead to the same results
*Be cautious: if no user is defined on a location form, those locations and the related stocks would be visible for everybody
    ''',
    'price': '50.00',
    'currency': 'EUR',
    'auto_install': False,
    'application':True,
    'author': 'IT Libertas',
    'website': 'https://itlibertas.com',
    'depends': [
        'stock',
    ],
    'data': [ 
        'security/ir.model.access.csv',
        'views/stock_view.xml',
        'views/res_users_view.xml',
            ],
    'qweb': [ 
    
            ],
    'js': [ 

            ],
    'demo': [ 

            ],
    'test': [ 

            ],
    'license': 'AGPL-3',
    'images': ['static/description/main.png'],
    'update_xml': [],
    'application':True,
    'installable': False,
    'private_category':False,
    'external_dependencies': {
    },

}
