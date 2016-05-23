{
    # Theme information
    'name' : 'Medical Equipment Management - Backend Theme',
    'category' : 'Theme/Backend',
    'version' : '1.1.18',
    'summary': 'Backend, Clean, Modern, Material, Theme',
    'description': """
Medical Equipment Management - Backend Theme
============================================
Tema backend dedicato al sistema di gestione
delle strutture mediche di SimplERP.
    """,
    'images': ['static/description/theme.jpg'],

    # Dependencies
    'depends': [
        'web',
    ],
    'external_dependencies': {},

    # Views
    'data': [
	'views/backend.xml'
    ],

    # Author
    'author' : '8cells - SimplERP Srl',
    'website' : 'https://simplerp.it',

    # Technical
    'installable': True,
    'auto_install': False,
    'application': False,
}