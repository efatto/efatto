# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Sergio Corato (<http://www.didotech.com>)
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
    "name" : "Fiscal Year Closing Template",
    "version" : "3.0.0.0",
    "author" : "Didotech",
    "website" : "http://www.didotech.com",
    "category" : "Generic Modules/Accounting",
    "description": """

Fiscal Year Closing Wizard Template for numeric pdc

    """,
    "license" : "AGPL-3",
    "depends" : [
                    "account_fiscal_year_closing",
                ],
    "init_xml" : [],
    "update_xml" : [
                    "data/account_journal.xml",
                    "data/account_template_fy.xml",
                    ],
    "active": False,
    "installable": True
}

