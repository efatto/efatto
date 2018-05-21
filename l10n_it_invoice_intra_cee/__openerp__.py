# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>)
#    Copyright (C) 2014 Didotech srl
#    Copyright (C) 2015-2017 Sergio Corato
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
##############################################################################

{
    'name': "Invoice Intra CEE",
    'version': '8.0.1.0.0',
    'category': 'Account',
    'description': "Manage Invoice for Intra CEE",
    'author': 'CoOpenERP <info@coopenerp.it>, Didotech srl <info@didotech.com>'
              ', Sergio Corato <info@efatto.it>',
    'website': 'https://www.efatto.it',
    'license': 'AGPL-3',
    "depends": [
        'base',
        'account',
        'account_voucher',
        'account_journal_sequence',
    ],
    "data": [
        'views/account_view.xml',
        'views/account_data.xml',
    ],
    "test": [
        'test/invoice_reverse_charge.yml',
    ],
    'installable': False,
}
