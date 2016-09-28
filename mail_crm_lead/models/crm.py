# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp.addons.base.res.res_partner import format_address
from openerp.osv import osv
from openerp.tools.translate import _
from openerp.addons.mail.mail_message import decode

AVAILABLE_PRIORITIES = [
    ('0', 'Very Low'),
    ('1', 'Low'),
    ('2', 'Normal'),
    ('3', 'High'),
    ('4', 'Very High'),
]


class crm_lead(format_address, osv.osv):
    _inherit = 'crm.lead'

    def message_new(self, cr, uid, msg, custom_values=None, context=None):
        """ Overrides mail_thread message_new that is called by the mailgateway
            through message_process.
            This override updates the document according to the email.
        """
        company = self.pool['res.users'].browse(cr, uid, uid).company_id
        if custom_values is None:
            custom_values = {}
        defaults = {
            'name': msg.get('body')[:20] or msg.get('subject') or _("No Subject"),
            'email_from': msg.get('reply_to', False) and msg.get('reply_to') or
            msg.get('from'),
            'email_cc': msg.get('cc'),
            'partner_id': msg.get('author_id', False) != company.id and
            msg.get('author_id', False) or False,
            'user_id': False,
            #'contact_name':
            #'description':
            #'referred':
        }
        if msg.get('author_id') and msg.get('author_id') != company.id:
            defaults.update(self.on_change_partner_id(cr, uid, None, msg.get('author_id'), context=context)['value'])
        if msg.get('priority') in dict(AVAILABLE_PRIORITIES):
            defaults['priority'] = msg.get('priority')
        defaults.update(custom_values)
        return super(crm_lead, self).message_new(cr, uid, msg, custom_values=defaults, context=context)


class MailThread(osv.AbstractModel):
    _inherit = 'mail.thread'

    def message_parse(self, cr, uid, message, save_original=False, context=None):
        msg_dict = super(MailThread, self).message_parse(
            cr, uid, message, save_original=save_original, context=context)

        if message.get('Reply-To'):
            msg_dict['reply_to'] = decode(message.get('Reply-To'))

        return msg_dict
