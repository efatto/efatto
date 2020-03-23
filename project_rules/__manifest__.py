# Copyright 2016-2020 Sergio Corato
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Project rules limit to followers and members or managed',
    'version': '12.0.1.0.1',
    'category': 'other',
    'author': 'Sergio Corato',
    'description': 'Change project rules: add favourite and set manager as an user, '
                   'viewing only project task managed or following or favourite.',
    'website': 'https://efatto.it',
    'license': 'LGPL-3',
    'depends': [
        'project',
    ],
    'data': [
        'security/project_security.xml',
    ],
    'installable': True
}
