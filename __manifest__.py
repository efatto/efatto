# Copyright (C) 2013 Stefano Siccardi creativiquadrati snc
# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Sale calendar state',
    'author': 'Sergio Corato',
    'website': 'https://efatto.it',
    'version': '12.0.1.0.0',
    'summary': 'Gestione calendario ordini di vendita con colori che corrispondono '
               'a stati',
    'depends': [
        'sale',
        'sale_stock',
        'sale_order_line_date',
        'web',
    ],
    'data': [
        'views/assets.xml',
        'views/orders_view.xml',
        # 'views/picking_view.xml',
        # 'views/sale_data.xml',

    ],
    'installable': True,
}
