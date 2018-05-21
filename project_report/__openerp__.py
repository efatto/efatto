# -*- coding: utf-8 -*-
##############################################################################
#
#    Project Reports
#    Copyright (C) 2016 January
#    1200 Web Development
#    http://1200wd.com/
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
    'name': "Project Reports",
    'summary': """Create reports of Projects Tasks and Issues""",
    'description': """
        Create reports of Projects Tasks and Issues
    """,
    'author': "1200 Web Development",
    'website': "http://1200wd.com",
    'category': 'Project',
    'version': '8.0.1.1',
    'depends': [
        'project',
        'project_issue',
    ],
    'data': [
        'views/project_view.xml',
        'reports/project_report.xml',
        'reports/project_task_report.xml',
        'reports/project_issue_report.xml',
    ],
    'price': 10.00,
    'currency': 'EUR',
    'demo': [],
    'installable': False,
    'auto_install': False,
    'application': False,
}
