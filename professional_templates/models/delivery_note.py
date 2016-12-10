# -*- coding: utf-8 -*-
from openerp import models, fields, api

class customized_dn_order(models.Model):
	_inherit=["stock.picking"]

	@api.model
	def _default_template(self):
	    company_obj = self.env['res.company']
	    company = self.env['res.users'].browse([self.env.user.id]).company_id
	    if not company.template_dn:
		def_tpl = self.env['ir.ui.view'].search([('name', 'like', 'Delivery Template' ), ('type', '=', 'qweb')], order='id asc', limit=1)
                company.write({'template_dn': def_tpl.id})
	    return company.template_dn or self.env.ref('stock.report_picking')
	
	
 	dn_logo = fields.Binary("Logo", attachment=True,
             help="This field holds the image used as logo for the delivery slip, if non is uploaded, the default logo set in the company settings will be used")
	templ_id = fields.Many2one('ir.ui.view', 'Delivery Slip Template', default=_default_template,required=False, 
		domain="[('type', '=', 'qweb'), ('name', 'like', 'Delivery Template' )]")
        odd = fields.Char('Odd parity Color', size=7, required=True, default=lambda self: self.env.user.company_id.odd, help="The background color for odd lines in the delivery slip")	
        even = fields.Char('Even parity Color', size=7, required=True, default=lambda self: self.env.user.company_id.even, help="The background color for even lines in the delivery slip" )	
        theme_color = fields.Char('Theme Color', size=7, required=True, default=lambda self: self.env.user.company_id.theme_color, help="The Main Theme color of the Delivery Slip. Normally this should be one of your official company colors")	
        theme_txt_color = fields.Char('Theme Text Color', size=7, required=True, default=lambda self: self.env.user.company_id.theme_txt_color, 
			help="The Text color of the areas with theme color. This should not be the same the theme color")	
        text_color = fields.Char('Text Color', size=7, required=True, default=lambda self: self.env.user.company_id.text_color, help="The text color of the order. Normally this\
			 should be one of your official company colors or default HTML text color")	
        name_color = fields.Char('Company Name Color', size=7, required=True, default=lambda self: self.env.user.company_id.name_color, help="The Text color of the Company Name. \
			Normally thisshould be one of your official company colors or default HTML text color")	
        cust_color = fields.Char('Customer Name Color', size=7, required=True, default=lambda self: self.env.user.company_id.cust_color, help="The Text color of the Customer Name. \
			Normally this should be one of your official company colors or default HTML text color")	

        header_font = fields.Selection([(x,str(x)) for x in range(1,51)], string="Header Font-Size(px):", default=lambda self: self.env.user.company_id.header_font, required=True)
        body_font = fields.Selection([(x,str(x)) for x in range(1,51)], string="Body Font-Size(px):", default=lambda self: self.env.user.company_id.body_font, required=True)
        footer_font = fields.Selection([(x,str(x)) for x in range(1,51)], string="Footer Font-Size(px):", default=lambda self: self.env.user.company_id.footer_font, required=True)
        font_family = fields.Char('Font Family:', default=lambda self: self.env.user.company_id.font_family, required=True)
        show_img = fields.Boolean('Display image in PDF report?', default=lambda self: self.env.user.company_id.show_img, help="Check this box in order to display the product image on the Delivery Note and Picking List")

