# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Attachment visibility',
    'version': '12.0.1.0.3',
    'category': 'other',
    'author': 'Sergio Corato',
    'description':
        'Limit visibility of attachment to creator user, excluding erp manager.',
    'website': 'https://github.com/sergiocorato/efatto',
    'license': 'LGPL-3',
    'depends': [
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/ir_attachment_security.xml',
    ],
    'installable': True,
}
