# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################
import logging
from openerp.exceptions import Warning
logger = logging.getLogger(__name__)

from openerp import models, fields, api

from openerp.tools.translate import _
meta_list =  [('Name', 'Name'), ('Category', 'Category'), ('Supplier', 'Supplier'), ('Description', 'Description')]
meta_fields_list = [('website_meta_title','Title'),('website_meta_description','Description'),('website_meta_keywords','Keywords')]
class website_seo_wizard(models.TransientModel):
	_name = 'website.seo.wizard'
			
	meta_value = fields.Selection(meta_list,string = "Meta Value", default = "Name", required=True)
	updated_meta_info = fields.Char()




	def add_meta_value(self,cr,uid,ids,context=None):
		return True
		# res= self.env['website.seo'].browse(context['active_id'])
		
		# meta_value = self.meta_value + res.multi_attribute_seperator
		# if context['update_field'] == 'Keywords' :
		# 	res.website_meta_keywords  += meta_value
			
		# elif context['update_field'] == 'Title' :
		# 	res.website_meta_title 	+= meta_value
			
		# elif context['update_field'] == 'Description' :
		# 	res.website_meta_description += meta_value
	@api.one
	def remove_meta_value(self, context):
		res= self.env['website.seo'].browse(context['active_id'])
		meta_value = self.meta_value + res.multi_attribute_seperator
		if context['update_field'] == 'Keywords' :
			pk =res.website_meta_keywords.replace(meta_value, "")
			res.write({'website_meta_keywords': pk})
			
			
			
		elif context['update_field'] == 'Title' :
			pk =res.website_meta_title.replace(meta_value, "")
			res.write({'website_meta_title': pk})
			
			
		elif context['update_field'] == 'Description' :
			pk =res.website_meta_description.replace(meta_value, "")
			res.write({'website_meta_description': pk})
			



			

		
		