# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Re-enable editable on purchase order line',
    'version': '12.0.1.0.0',
    'category': 'other',
    'author': 'Sergio Corato',
    'description': 'Warning: this module make impossible to write formatted note '
                   'on purchase order line.',
    'website': 'https://github.com/sergiocorato/efatto',
    'license': 'AGPL-3',
    'depends': [
        'purchase_comment_template',
    ],
    'data': [
        'views/purchase.xml',
    ],
    'installable': True,
}
