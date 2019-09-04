# -*- coding: utf-8 -*-
#
#
#    Copyright (C) 2016-2019 Sergio Corato
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
    'name': 'Italian central journal fix',
    'version': '8.0.1.2.4',
    'category': 'other',
    'author': 'Sergio Corato',
    'description': 'Italian Central journal various fix',
    'website': 'http://www.efatto.it',
    'license': 'AGPL-3',
    'depends': [
        'l10n_it_central_journal',
    ],
    'data': [
        'report/report_account_central_journal.xml',
    ],
    'installable': True
}
