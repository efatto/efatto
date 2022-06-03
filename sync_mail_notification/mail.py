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

import datetime
from openerp import SUPERUSER_ID, api
from openerp.osv import osv, orm, fields

class mail_notification(osv.Model):
    _inherit = 'mail.notification'

    _columns = {
        'is_notified': fields.boolean('Notified')
    }

    _defaults = {
        'is_notified': False
    }

    #------------------------------------------------------
    # Notification 
    #------------------------------------------------------
    @api.cr_uid_ids_context
    def get_message_notification(self, cr, uid, context=None):
        notification_data = {}
        message_obj = self.pool.get('mail.message')
        current_date = datetime.datetime.utcnow()
        delta = datetime.timedelta(minutes=5)
        before_time = (current_date - delta).strftime("%Y-%m-%d %H:%M:%S")
        msg_ids = message_obj.search(cr, uid, [('date', '>=', before_time), ('date', '<', current_date.strftime("%Y-%m-%d %H:%M:%S"))], context=context)
        if msg_ids:
            user_id = self.pool['res.users'].browse(cr, SUPERUSER_ID, uid, context=context)
            domain = [('partner_id', '=', user_id.partner_id and user_id.partner_id.id), ('message_id', 'in', msg_ids), ('is_read', '=', False), ('is_notified', '=', False)]
            notif_ids = self.search(cr, uid, domain, context=context) or False
            for notif_id in self.browse(cr, uid, notif_ids, context=context):
                message_id = message_obj.browse(cr, uid, notif_id.message_id and notif_id.message_id.id or False, context=context)
                notification_data[notif_id.id] = {
                    'id': notif_id.id,
                    'email_from': message_id.email_from.split('<')[0],
                    'subject': message_id.subject or '-- No Subject --',
                    'company_id': user_id.company_id.id or False
                }
            return notification_data or {}
        return {}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

