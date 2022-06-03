# -*- coding: utf-8 -*-
from openerp import models, fields, api

class customized_picking_slip(models.Model):
	_inherit=["stock.picking"]

	@api.model
	def _default_picking_template(self):
	    company_obj = self.env['res.company']
	    company = self.env['res.users'].browse([self.env.user.id]).company_id
	    if not company.template_pk:
		def_tpl = self.env['ir.ui.view'].search([('name', 'like', 'Picking Template' ), ('type', '=', 'qweb')], order='id asc', limit=1)
                company.write({'template_pk': def_tpl.id})
	    return company.template_pk or self.env.ref('stock.report_picking')
	
 	pk_logo = fields.Binary("Logo", attachment=True,
             help="This field holds the image used as logo for the Picking, if non is uploaded, the default logo set in the company settings will be used")
	templ_pk_id = fields.Many2one('ir.ui.view', 'Picking Slip Template', default=_default_picking_template,required=False, 
		domain="[('type', '=', 'qweb'), ('name', 'like', 'Picking Template' )]")

	def do_print_picking(self, cr, uid, ids, context=None):
        	'''This function prints the picking list'''
        	context = dict(context or {}, active_ids=ids)
        	self.write(cr, uid, ids, {'printed': True}, context=context)
        	return self.pool.get("report").get_action(cr, uid, ids, 'professional_templates.report_picking', context=context)

