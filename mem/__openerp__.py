# -*- coding: utf-8 -*-
##############################################################################
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
    'name' : 'Apparecchiature Medicali',
    'version' : '0.1',
    'author' : 'OpenERP S.A. - SimplERP Srl',
    'sequence': 110,
    'category': 'Medical Equipment Management',
    'website' : 'https://simplerp.it',
    'summary' : 'Medical, Equipment, Management',
    'description' : """
Apparecchiature Medicali
========================
Questo modulo consente di gestire le apparecchiature elettromedicali,
i contratti di assistenza associati alle apparecchiature, i servizi,
i log sul funzionamento, i costi d'esercizio ed altri aspetti direttamente
collegati al settore medico e ospedaliero.

Principali Caratteristiche
-------------
* Aggiungere apparecchiature elettromedicali alle dotazioni della struttura
* Gestire i contratti di assistenza e manutenzione relativi alle apparecchiature
* Prtomemoria per le scadenze di contratti, revisioni, manutenzioni ecc...
* Gestire servizi, log, valori dei contatori...
* Visualizzazione dei costi associati a ciascuna apparecchiatura o ad un tipo di servizio
* Analisi grafica dei costi
""",
    'depends' : [
        'base',
        'mail',
        'board'
    ],
    'data' : [
        'security/mem_security.xml',
        'security/ir.model.access.csv',
        'mem_view.xml',
        'mem_cars.xml',
        'mem_data.xml',
        'mem_board_view.xml',
    ],

    'demo': ['mem_demo.xml'],

    'installable' : True,
    'application' : True,
}
