# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Clear ICT Solutions <info@clearict.com>.
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify it
#    under the terms of the GNU Affero General Public License as published by
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
    'name': 'Apparecchiature Medicali - Dipartmenti',
    'summary': 'Associa le Apparecchiature Medicali ad un dipartmento',
    'description': """
Apparecchiature Medicali - Dipartmenti
======================================
Questo modulo consente di associare un'Apparecchiatura Elettromedicale ad un
Dipartimento. In questo caso, solo un Manager collegato a quello stesso dipartimento
potrà gestire l'Apparecchiature.
    """,
    'author': 'Clear ICT Solutions, SimplERP Srl',
    'website': 'https://simplerp.it',
    'version': '1.0',
    'category': 'Medical Equipment Management',
    'depends': [
        'mem',
        'hr',
    ],
    'data': [
        'security/mem.xml',
        'security/ir.model.access.csv',
        'views/mem.xml',
    ],
    'test': [
    ],
    'demo_xml': [
    ],
    'installable': True,
    'active': False,
}
