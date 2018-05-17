# -*- coding: utf-8 -*-
#
#
#    Copyright (C) 2016-2017 Sergio Corato
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
{
    'name': 'Italia account extension',
    'version': '8.0.1.0.0',
    'category': 'other',
    'author': 'Sergio Corato',
    'website': 'http://www.efatto.it',
    'license': 'AGPL-3',
    'description': 'Italian account fixes: '
                   '- add and set standard sale and purchase journal for '
                   'default fiscal position;'
                   '- set group invoice lines for all invoice journal;'
                   '- set update_posted = True for all journals;'
                   '- set entry_posted = True for cash/bank journals;'
                   '- modify basic qweb template header and footer;'
                   '',
    'depends': [
        'account_accountant',
        'l10n_it_account',
        'account_cancel',
        'sale',
    ],
    'data': [
        'views/account.xml',
        'views/account_report.xml',
    ],
    'installable': True,
    'post_init_hook': 'post_init_hook',
}
