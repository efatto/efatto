# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
import crm
from openerp.addons.base.res.res_partner import format_address
from openerp.osv import fields, osv, orm
import xml.etree.ElementTree as ET
from openerp.tools.translate import _


class crm_lead(format_address, osv.osv):
    _inherit = "crm.lead"

    def message_new(self, cr, uid, msg, custom_values=None, context=None):
        """ Overrides mail_thread message_new that is called by the mailgateway
            through message_process.
            This override updates the document according to the email.
        """
        if custom_values is None:
            custom_values = {}
        b = msg.get('body')
        e = b.replace('<br>', '').replace('\r\n', '')
        body = ET.fromstring(e)
        email_from = False
        if msg.get('from') != msg.get('to'):
            email_from == msg.get('from')
        elif msg.get('reply_to'):
            email_from == msg.get('reply_to')

        defaults = {
            'name':  msg.get('subject') or _("No Subject"),
            'email_from': email_from,
            'email_cc': msg.get('cc'),
            'partner_id': msg.get('author_id', False),
            'user_id': False,
            #'contact_name':
            #'email_from':
            #'description':
            #'referred':
        }
        if msg.get('author_id'):
            defaults.update(self.on_change_partner_id(cr, uid, None, msg.get('author_id'), context=context)['value'])
        if msg.get('priority') in dict(crm.AVAILABLE_PRIORITIES):
            defaults['priority'] = msg.get('priority')
        defaults.update(custom_values)
        return super(crm_lead, self).message_new(cr, uid, msg, custom_values=defaults, context=context)
