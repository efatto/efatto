# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Sale Bookmark',
    'version': '12.0.1.0.4',
    'author': 'Sergio Corato',
    'category': 'Tools',
    'license': 'AGPL-3',
    'depends': [
        'product',
        'sale',
        'stock',
    ],
    'description': "Add bookmarked info to product availability. A quotation can be "
                   "considered bookmarked for the customer if in a specific state "
                   "or marked manually by the user. "
                   "Default bookmark is when quotation is in sent state, to remove this"
                   " default delete the key 'sale.order.bookmark.state' in config "
                   "parameters and mark manually order with bookmark flag.",
    'data': [
        'data/ir_config_parameter.xml',
        'views/product.xml',
        'views/sale.xml',
    ],
    'installable': True,
    'post_init_hook': 'post_init_hook',
}
