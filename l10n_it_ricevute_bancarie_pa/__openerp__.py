# -*- coding: utf-8 -*-
#
#
#    Copyright (C) 2017-2018 Sergio Corato.
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
    'name': 'Ricevute bancarie pa',
    'version': '8.0.1.0.0',
    'category': 'other',
    'author': 'Sergio Corato',
    'website': 'http://www.efatto.it',
    'description': 'Ricevute bancarie bank riba with cig cup',
    'license': 'AGPL-3',
    'depends': [
        'account_bank',
        'account_payment_term_month',
        'l10n_it_abicab',
        'l10n_it_ricevute_bancarie_ext',
        'l10n_it_fatturapa_out',
    ],
    'data': [
        'views/riba_view.xml',
    ],
    'installable': True
}
