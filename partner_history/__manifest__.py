# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Partner history',
    'version': '12.0.1.0.1',
    'category': 'Accounting & Finance',
    'author': 'Sergio Corato',
    'website': 'https://efatto.it',
    'license': 'AGPL-3',
    'description': 'Partner name history',
    'depends': [
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/partner.xml',
    ],
    'installable': True,
}
