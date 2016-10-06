# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
#    Copyright (C) 2011-today Synconics Technologies Pvt. Ltd. (<http://www.synconics.com>)
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
    "name": "Mail Push Notification",
    "version": "1.0",
    "author": "Synconics Technologies Pvt. Ltd.",
    "website": "www.synconics.com",
    "version": "1.0",
    "catagory": "Social Network",
    "complexity": "easy",
    "summary": "Odoo Mail Push Notification",
    "description": """
   The push notification shows at the status bar that you have received a new mail message. This notification will make you aware about the message and you can take action on it at the same moment.
    """,
    "depends": ["mail"],
	"data": ["views/mail_notification_view.xml"],
    "qweb": [],
    "installable": True,
    "auto_install": False
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: