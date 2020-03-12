# Copyright 2019 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Italy - PDC 7 number generic',
    'version': '12.0.0.0.1',
    'category': 'Localization',
    'description': """
    Italy PDC with 7 number generic
    """,
    'author': 'Sergio Corato',
    'website': 'https://efatto.it',
    'license': 'LGPL-3',
    "depends": [
        'account',
        'base_vat',
        'base_iban',
    ],
    "data": [
        'data/l10n_it_chart_data.xml',
        'data/data_account_type.xml',
        'data/account.account.template.csv',
        'data/account.tax.group.csv',
        'data/account.tax.template.csv',
        'data/account.fiscal.position.template.csv',
        'data/account.fiscal.position.tax.template.csv',
        'data/account.chart.template.csv',
        'data/account_chart_template_data.xml',
    ],
    "installable": True,
}
