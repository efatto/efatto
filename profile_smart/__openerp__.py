# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 SimplERP srl (<http://www.simplerp.it>).
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
    'name': 'Italy - SimplERP Srl profile Smart',
    'version': '8.0.0.0.1',
    'category': 'other',
    'description': """
    Profilatura SimplERP
    """,
    'author': 'SimplERP SRL',
    'website': 'http://www.simplerp.it',
    'license': 'AGPL-3',
    "depends": [
        'account_analytic_analysis',
        'account_cancel',
        'base_setup',
        'base_iban',
        'country_data_it',
        'disable_openerp_online',
        'document',
        'document_carddav',
        'l10n_it_base_location_geonames_import',
        'project',
        'project_timesheet',
        'hr_timesheet',
        'hr_timesheet_sheet',
        'hr_expense',
        'web_debranding',
    ],
    "data": [
        'security/profile_smart_security.xml',
        #'security/ir.model.access.csv',
        'views/account_analytic_view.xml',
        'views/hr_view.xml',
        'views/hr_workflow.xml',
        'views/smart_view.xml',
    ],
    "installable": True,
}
