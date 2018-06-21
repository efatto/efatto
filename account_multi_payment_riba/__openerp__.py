# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016-2018 Sergio Corato
#    Copyright (C) 2013 Didotech srl (<http://www.didotech.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Account Multi payment riba',
    'version': '8.0.1.0.0',
    'category': 'Generic Modules/Payment',
    'author': 'Sergio Corato',
    'description': "Exclude riba from multi payment search view",
    'website': 'http://www.efatto.it',
    'license': 'AGPL-3',
    'depends': [
        'account_multi_payment',
        'l10n_it_ricevute_bancarie',
    ],
    'data': [
        'views/statement.xml',
    ],
    'installable': True
}
