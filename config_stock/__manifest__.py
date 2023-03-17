# Copyright 2019 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Module to configure stock',
    'version': '12.0.1.0.1',
    'category': 'other',
    'description': """
Module to configure stock.
Add the next groups to base user:
* stock.group_stock_multi_locations
* stock.group_stock_adv_location
* uom.group_uom
It also set invoice policy default to delivery.
""",
    'author': 'Sergio Corato',
    'website': 'https://github.com/sergiocorato/efatto',
    'license': 'LGPL-3',
    'depends': [
        'stock',
    ],
    'data': [
        'data/group.xml',
    ],
    'installable': True
}
