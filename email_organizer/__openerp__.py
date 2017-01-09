# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014-2015 Augustin Cisterne-Kaas (ACK Consulting Limited)
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
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{'name': 'Email Organizer Pro',
 'version': '0.1',
 'category': 'Social Network',
 'depends': ['web_polymorphic_field', 'mail'],
 'author': 'Augustin Cisterne-Kaas',
 'description': """
This module allows you to assign a message to an existing or
a new resource dynamically.

You can configure the available model through
"Settings" -> "Technical" -> "Email Organizer"
""",
 # 'license': 'LGPL-3',
 'currency': 'EUR',
 'price': 9,
 'data': ['wizard/wizard_email_organizer_view.xml',
          'model_view.xml',
          'views/email_organizer.xml'],
 'images': ['images/main.png'],
 'qweb': [
     'static/src/xml/email.xml'
 ],
 'installable': True,
 'application': True}
