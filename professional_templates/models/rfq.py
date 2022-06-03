# -*- coding: utf-8 -*-
from openerp import models, fields, api

class customized_rfq(models.Model):
	_inherit=["purchase.order"]

	@api.model
	def _default_rfq_template(self):
	    company_obj = self.env['res.company']
	    company = self.env['res.users'].browse([self.env.user.id]).company_id
	    if not company.template_rfq:
		def_tpl = self.env['ir.ui.view'].search([('name', 'like', 'RFQ Template' ), ('type', '=', 'qweb')], order='id asc', limit=1)
                company.write({'template_rfq': def_tpl.id})
	    return company.template_rfq or self.env.ref('purchase.report_purchasequotation_document')
	
 	rfq_logo = fields.Binary("Logo", attachment=True,
             help="This field holds the image used as logo for the RFQ, if non is uploaded, the default logo define in the company settings will be used")
	templ_rfq_id = fields.Many2one('ir.ui.view', 'RFQ Template', default=_default_rfq_template,required=False, 
		domain="[('type', '=', 'qweb'), ('name', 'like', 'RFQ Template' )]")

	@api.multi
    	def print_quotation(self):
        	self.write({'state': "sent"})
        	return self.env['report'].get_action(self, 'professional_templates.rfq')

