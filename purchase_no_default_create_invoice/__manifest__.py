# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Remove default create invoice button',
    'version': '12.0.1.0.0',
    'category': 'other',
    'description': """
    Default create invoice button in purchase order is hidden as new button create
    batch invoice is available.
    """,
    'author': 'Sergio Corato',
    'website': 'https://github.com/sergiocorato/efatto',
    'license': 'AGPL-3',
    'depends': [
        'purchase_batch_invoicing',
    ],
    'data': [
        'views/purchase.xml',
    ],
    'installable': True,
}
