# -*- coding: utf-8 -*-
##############################################################################
#
#    Closemarketing Software Solutions and Services
#    Copyright (C) 2012-2013 Closemarketing Odoo Experts(<https://www.closemarketing.es>).
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
    "name" : "CRM Lead Website Social",
    "version" : "1.1.1",
    "depends" : ["base",'crm'],
    "author" : "closemarketing",
    "description": """'Adds Social Media in Leads, Opportunities and Partners.'
    """,
    "website" : "",
    'images': [],
    "category" : "",
    'summary': 'CRM Lead Website Social',
    "demo" : [],
    "data" : [
        'crm_lead_website_social_view.xml',
        'crm_lead_view.xml',
    ],
    'auto_install': False,
    "installable": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


