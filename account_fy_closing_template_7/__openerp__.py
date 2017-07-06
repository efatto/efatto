# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013-2017 Sergio Corato
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
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
    "name" : "Fiscal Year Closing Template for pdc with 7 number",
    "version" : "8.0.1.0.0",
    "author" : "Sergio Corato",
    "website" : "http://www.efatto.it",
    "category" : "Generic Modules/Accounting",
    "description": "Fiscal Year Closing Wizard Template for pdc with 7 number",
    "license": "AGPL-3",
    "depends": [
        "account_fiscal_year_closing",
    ],
    "data": [
        "data/account_journal.xml",
        "data/account_template_fy.xml",
    ],
    "installable": True
}

