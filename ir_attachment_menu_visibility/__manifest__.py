# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Attachment menu visibility',
    'version': '12.0.1.0.0',
    'category': 'other',
    'author': 'Sergio Corato',
    'description':
        'Limit visibility of attachment to creator user, excluding erp manager.',
    'website': 'https://efatto.it',
    'license': 'AGPL-3',
    'depends': [
        'base',
    ],
    'data': [
        'security/ir_attachment_security.xml',
    ],
    'installable': True,
}
