# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 B-Informed B.V. (<http://b-informed.nl>).
#    Author: Roel Adriaans
#
#	 This module has been translated/tested/edited to fit SimplERP
#	 requirements and features (<http://www.simplerp.it>).
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
    'name': 'Disabilita indicizzazione sito web',
    'summary': 'Modifica il file robots.txt affinchè il sito web non venga indicizzato',

    'version': '1.0',
    'author': 'B-Informed B.V.',
    'complexity': 'normal',
    'description': """
Questo modulo modifica il file robots.txt al fine di bloccare l'indicizzazione da parte dei motori di ricerca.

Questa funzionalità risulta estremamente utile nell'integrazione di sistemi di test o siti web che non si desidera vengano indicizzati.
    """,
    'category': 'Website',
    'depends': [
        'website',
    ],
    'data': [
        'views/disable_robots.xml',
    ],
    'auto_install': False,
}
