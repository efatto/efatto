# Copyright 2019 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Module to configure mrp',
    'version': '12.0.1.0.0',
    'category': 'other',
    'description': """
Module to configure stock.
Add the next groups to base user:
- mrp.group_mrp_routings
""",
    'author': 'Sergio Corato',
    'website': 'https://github.com/sergiocorato/efatto',
    'license': 'AGPL-3',
    'depends': [
        'mrp',
    ],
    'data': [
        'data/group.xml',
    ],
    'installable': True
}
