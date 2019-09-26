# Copyright 2019 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Module to configure stock',
    'version': '12.0.1.0.0',
    'category': 'other',
    'description': """
Module to configure stock.
Add the next groups to base user:
* stock.group_lot_on_delivery_slip
* stock.group_stock_multi_locations
* stock.group_stock_production_lot
* stock.group_stock_adv_location
* uom.group_uom
* product.group_stock_packaging
It also set invoice policy default to delivery.
""",
    'author': 'Sergio Corato',
    'website': 'https://efatto.it',
    'license': 'LGPL-3',
    'depends': [
        'stock',
    ],
    'data': [
        'data/group.xml',
    ],
    'installable': True
}
