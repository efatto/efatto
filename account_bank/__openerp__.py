# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Didotech SRL (<http://www.didotech.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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
    'name': 'Bank for riba and payment in partner',
    'version': '8.1.0.0.0',
    'category': 'Localisation',
    'author': 'Didotech SRL, SimplERP srl',
    'website': 'http://www.simplerp.it',
    'license': 'AGPL-3',
    "depends": [
        'account',
    ],
    "data": [
        'security/security.xml',
        'views/account_invoice_view.xml',
    ],
    "installable": True
}
