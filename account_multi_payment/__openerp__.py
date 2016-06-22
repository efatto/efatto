# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Sergio Corato - SimplERP srl (<http://www.simplerp.it>)
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
    'name': 'Account Multi payment',
    'version': '8.0.1.0.0',
    'category': 'Generic Modules/Payment',
    'author': 'Sergio Corato - SimplERP SRL',
    'description': """

    Functionalities:

    - Add grouped multi payment to bank statement

    """,
    'website': 'http://www.simplerp.it',
    'license': 'AGPL-3',
    'depends': [
        'account',
        'account_voucher',
        'account_analytic_analysis',
    ],
    'data': [
        'views/payment_view.xml',
    ],
    'installable': True
}
