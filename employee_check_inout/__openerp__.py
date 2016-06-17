# -*- encoding: utf-8 -*-
##############################################################################
#    Copyright (c) 2012 - Present Acespritech Solutions Pvt. Ltd.
#    Author: <info@acespritech.com>
#    Copyright (C) 2016 Sergio Corato - SimplERP srl (<http://www.simplerp.it>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of the GNU General Public License is available at:
#    <http://www.gnu.org/licenses/gpl.html>.
#
##############################################################################

{
    'name': 'Employee CheckIn/CheckOut',
    'version': '8.0.0.1.0',
    'category': 'HR',
    'summary': 'HR: Employee Check In-Out',
    'description': """
Allows to keep track of employee attendance and can print attendance report.
    """,
    'author': "Acespritech Solutions Pvt. Ltd., SimplERP Srl",
    'website': "www.acespritech.com",
    'images': ['static/description/main_screenshot.png'],
    'depends': ['base', 'hr_attendance', 'hr_timesheet'],
    'data': [
        'wizard/wizard_weekly_hours_view.xml',
        'views/print_weekly_hours_template.xml',
        'report/report.xml',
        'views/employee_kanban_view.xml',
        'views/hr_employee_view.xml'
    ],
    'installable': True,
}
