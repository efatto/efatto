# Copyright 2018 Alex Comba - Agile Business Group
# Copyright 2016-2018 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Sale MRP info Link',
    'summary': 'Show info on manufacturing orders generated from sales order',
    'version': '12.0.1.0.2',
    'category': 'Sales Management',
    'website': 'https://efatto.it',
    'author': 'Sergio Corato (Efatto.it)',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'mrp_sale_info',
    ],
    'data': [
        'views/sale_order.xml',
    ],
    'post_init_hook': 'post_init_hook',
}
