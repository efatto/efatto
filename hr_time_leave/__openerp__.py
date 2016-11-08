# -*- coding: utf-8 -*-
# #############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
    'name': 'Time Leave Management',
    'version': '1.0',
    'author': 'Khaled Hamed',
    'category': 'Human Resources',
    'sequence': 11,
    'summary': 'Time Leave Requests/Permissions',
    'website': 'https://www.grandtk.com',
    'description': """
Manage HR Time Leaves/Permissions and allocation requests
=====================================

This module is a modified version of hr_holidays in order to track employees's time permissions instead of days as most
of companies allow hourly leaves each month.

This application controls the time leave permissions of your company. It allows employees to request time leave.

Managers can review requests for time leaves and approve or reject them.

You can keep track of leaves in different ways by following reports:

* Time Leaves Summary
* Time Leaves by Department


As hr_holidays, synchronization with an internal agenda (Meetings of the CRM module) is also possible in order to automatically create a meeting when a time request is accepted by setting up a type of meeting in Leave Type.
""",
    # 'images': ['images/hr_allocation_requests.jpeg', 'images/hr_leave_requests.jpeg', 'images/leaves_analysis.jpeg'],
    'depends': ['hr', 'calendar', 'resource', 'hr_holidays'],
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'hr_time_leave_workflow.xml',
        'hr_time_leave_view.xml',
        'hr_time_leave_data.xml',
        'hr_time_leave_report.xml',
        # 'report/hr_time_leave_report_view.xml',
        # 'report/available_time_leave_view.xml',
        'wizard/hr_time_leave_summary_department_view.xml',
        'wizard/hr_time_leave_summary_employees_view.xml',
    ],
    # 'demo': ['hr_time_leave_demo.xml', ],
    # 'qweb': [
    #     'static/src/xml/*.xml',
    # ],
    # 'test': ['test/test_hr_time_leave.yml',
    #          'test/hr_time_leave_report.yml',
    # ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 10.00,
    'currency': 'EUR',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
