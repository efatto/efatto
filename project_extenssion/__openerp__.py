# -*- coding: utf-8 -*-
#
#
#    Copyright (C) 2016 Sergio Corato - SimplERP srl (<http://www.simplerp.it>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
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
#
{
    "name": "Project Tasks Start/Stop",
    "summary": "Starts and stops the project tasks easily",
    "version": "8.0.0.1",
    "author": "SimplERP SRL, Opencloud",
    "license": "LGPL-3",
    "website": "http://www.simplerp.it",
    "category": "Project",
    "depends": [
        "project",
        'web_kanban',
        'web'
    ],
    "data": [
        'project_extenssion_view.xml',
        'email_data.xml',
     ],
    'installable': False,
    'images': ['images/imagem_project_extension.png'],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
