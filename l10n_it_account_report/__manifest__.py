# -*- coding: utf-8 -*-
# Copyright 2019 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Italia account better report',
    'version': '10.0.1.0.0',
    'category': 'Account',
    'author': 'Sergio Corato',
    'website': 'https://efatto.it',
    'license': 'LGPL-3',
    'description': 'Modify basic qweb template header and footer for italian '
                   'better usage.',
    'depends': [
        'l10n_it_account',
    ],
    'data': [
        'views/account_report.xml',
    ],
    'installable': True,
}
