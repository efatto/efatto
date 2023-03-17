# Copyright 2019-2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Sale delivered percent',
    'version': '12.0.1.0.0',
    'category': 'Sale Management',
    'description':
        'Compute delivered quantity on sale order line on percent if product has '
        'invoice policy on order, has u.m. of category unit and is a service that '
        'generate task.',
    'author': 'Sergio Corato',
    'website': 'https://github.com/sergiocorato/efatto',
    'depends': [
        'analytic',
        'sale_timesheet',
        'project',
    ],
    'data': [
    ],
    'installable': True,
}
