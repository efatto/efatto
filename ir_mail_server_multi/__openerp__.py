# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016 Sergio Corato - SimplERP SRL
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
    'name': 'Check and use mail server corresponding to user domain'
            ' when sending mail',
    'version': '8.0.1.0.0',
    'category': 'Extra Tools',
    'description': 'Check and use mail server corresponding to user domain'
' when sending mail. Search is done on name of outgoing mail server, so if it'
' is found a server with the exact name it will be used, else it works as '
'standard. This is a simple workaround for missing feature.',
    'author': 'Sergio Corato - Simplerp srl',
    'website': 'http://www.simplerp.it',
    'depends': [
    ],
    'data': [
    ],
    'installable': False,
}
