# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010 OpenERP s.a. (<http://openerp.com>).
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
    'name': 'Soltein Auto Refresh Views',
    'version': '0.1',
    'category': 'web',
    'description': """This module use the auto_refresh field of OpenERP actions to set a time based refresh of views used on the actions.
    Useful for auto-refresh Trees, Forms, Kanban, Graphs, Calendar""",
    'author': 'aekroft@gmail.com',
    'website': 'www.soltein.org',
    'depends': ['base', 'web', 'web_calendar', 'web_graph', 'web_kanban'],
    'data': ['assets.xml'],
    'active': False,
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
