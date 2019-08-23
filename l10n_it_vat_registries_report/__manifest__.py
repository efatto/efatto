# -*- coding: utf-8 -*-
# Copyright 2019 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Italia vat registries customized report',
    'version': '10.0.1.0.1',
    'category': 'Account',
    'author': 'Sergio Corato',
    'website': 'https://efatto.it',
    'license': 'LGPL-3',
    'description': 'Italia customized vat registries report',
    'depends': [
        'l10n_it_vat_registries',
    ],
    'data': [
        'views/vat_registries_report.xml',
    ],
    'installable': True
}
