# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################

##############################################################################

from openerp.osv import osv
from openerp.osv import fields

class crm_lead(osv.osv):
    '''
    Add social media to lead
    '''
    _name = 'crm.lead'
    _inherit = 'crm.lead'
    _description = 'Add website and social media to Partner, Leads and Opportunities'

    _columns = {
        'facebook':fields.char('Facebook', size=64, required=False, readonly=False),
        'twitter':fields.char('Twitter', size=64, required=False, readonly=False),
        'skype':fields.char('Skype', size=64, required=False, readonly=False),
        'website': fields.char('Website', help="Website of Partner or Company"),
        'linkedin':fields.char('Linkedin', size=64, required=False, readonly=False),
    }
    
    def goto_facebook(self, cr, uid, ids, context=None):
        partner_obj = self.pool.get('res.partner')
        partner = partner_obj.browse(cr, uid, ids, context=context)[0]
        if partner.facebook:
            good_starting_urls = ['https://facebook.com/', 'https://www.facebook.com/', \
                                  'http://facebook.com/', 'http://www.facebook.com/']
            non_protocol_starting_urls = ['facebook.com/', 'www.facebook.com/']
            
            if any(map(lambda x: partner.facebook.startswith(x), good_starting_urls)):
                url = partner.facebook
            elif any(map(lambda x: partner.facebook.startswith(x), non_protocol_starting_urls)):
                url = 'https://' + partner.facebook
            else:
                url = 'https://www.facebook.com/' + partner.facebook
            
            return {'type': 'ir.actions.act_url', 'url': url, 'target': 'new'}
    
    def goto_twitter(self, cr, uid, ids, context=None):
        partner_obj = self.pool.get('res.partner')
        partner = partner_obj.browse(cr, uid, ids, context=context)[0]
        
        if partner.twitter:
            good_starting_urls = ['https://twitter.com/', 'https://www.twitter.com/', \
                                  'http://twitter.com/', 'http://www.twitter.com/']
            non_protocol_starting_urls = ['twitter.com/', 'www.twitter.com/']
            
            if any(map(lambda x: partner.twitter.startswith(x), good_starting_urls)):
                url = partner.twitter
            elif any(map(lambda x: partner.twitter.startswith(x), non_protocol_starting_urls)):
                url = 'https://' + partner.twitter
            else:
                url = 'https://www.twitter.com/' + partner.twitter
            
            return {'type': 'ir.actions.act_url', 'url': url, 'target': 'new'}
        
    def goto_linkedin(self, cr, uid, ids, context=None):
        partner_obj = self.pool.get('res.partner')
        partner = partner_obj.browse(cr, uid, ids, context=context)[0]
        
        if partner.linkedin:
            good_starting_urls = ['https://linkedin.com/', 'https://www.linkedin.com/', \
                                  'http://linkedin.com/', 'http://www.linkedin.com/']
            non_protocol_starting_urls = ['linkedin.com/', 'www.linkedin.com/']
            
            if any(map(lambda x: partner.linkedin.startswith(x), good_starting_urls)):
                url = partner.linkedin
            elif any(map(lambda x: partner.linkedin.startswith(x), non_protocol_starting_urls)):
                url = 'https://' + partner.linkedin
            else:
                url = 'https://www.linkedin.com/' + partner.linkedin
            
            return {'type': 'ir.actions.act_url', 'url': url, 'target': 'new'}
        
        
    def on_change_partner_id(self, cr, uid, ids, partner_id, context=None):
        res = super(crm_lead, self).on_change_partner_id(cr, uid, ids, partner_id, context=context)
        partner = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
        res['value'].update({'facebook': partner.facebook, 'twitter':partner.twitter,'skype':partner.skype,'linkedin':partner.linkedin, 'website':partner.website})
        return res








