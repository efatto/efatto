# Copyright 2015 Angel Moya <angel.moya@domatix.com>
# Copyright 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Contract Show Invoiced Amount',
    'summary': 'Show invoiced amount in contract invoiced button',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Sergio Corato',
    'website': 'https://github.com/sergiocorato/efatto',
    'depends': ['account', 'contract'],
    'category': 'Sales Management',
    'data': [
        'views/contract.xml',
    ],
    'installable': True,
}
