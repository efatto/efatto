# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Purchase tag on state',
    'version': '12.0.1.0.0',
    'category': 'other',
    'author': 'Sergio Corato',
    'description': 'Add purchase tag linked to order state.',
    'website': 'https://github.com/sergiocorato/efatto',
    'license': 'AGPL-3',
    'depends': [
        'purchase',
        'web_widget_color',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/purchase.xml',
    ],
    'installable': True,
}
