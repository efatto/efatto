# Copyright 2019-2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Account analytic SAL',
    'version': '12.0.1.0.0',
    'category': 'Extra Tools',
    'description':
        'Account analytic SAL',
    'author': 'Sergio Corato',
    'website': 'https://efatto.it',
    'depends': [
        'analytic',
        'contract',  # _show_invoice
        # 'contract_show_sale', inutile direi
        'hr_timesheet',
        'project',
        'contacts',
        'sale_delivered_percent',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account.xml',
        'views/project.xml',
        'views/sale.xml',
    ],
    'installable': True,
}
