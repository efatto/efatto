# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################

from openerp.osv import fields,osv
from openerp.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)
from openerp.exceptions import Warning

class website_seo_config_settings(osv.osv_memory):
	_name = 'website.seo.config.settings'
	_inherit = 'website.config.settings'
	_columns = {
		'default_multi_attribute_seperator':fields.char('Multi-Attribute Separator', default_model = 'website.seo', help = """Multi-Attribute Separator.""" ,  required = 1),
		'default_multi_value_seperator':fields.char('Multi-Value Separator', default_model = 'website.seo' , help = """Multi-Value Separator.""",  required = 1),
		'wk_seo_website_meta_title_size':fields.integer('Max Length Of Title', help = """The maximum length of "title" meta-tags.""", required = 1),     
		'wk_seo_website_meta_description_size':fields.integer('Max Length of Description', help = """The maximum length of "Description" meta-tags.""", required = 1),
		'wk_seo_website_meta_keywords_size':fields.integer('Max Length of Keyword', help = """The maximum length of "Keywords" meta-tags.""", required = 1),
		'wk_seo_website_meta_keywords_number':fields.integer('Max No. of Keywords', help = """The maximum length of "Description" meta-tags.""" , required = 1) ,
		'wk_seo_website_meta_image_alt_text_size':fields.char('Image Alt-Text', help = """Add Alt Text to an Image.""" , default = 'Records Name', readonly = 1),
	}
	def get_default_seo_config_fields(self, cr, uid, ids,fields, context=None):
		ir_values = self.pool.get('ir.values')
		seo_config_values_list_tuples = ir_values.get_defaults(cr, uid, 'website.seo')	
		seo_config_values = {}
		for item in seo_config_values_list_tuples:
			seo_config_values.update({item[1]:item[2]})
		return seo_config_values
		
		

	def set_seo_config_fields(self, cr, uid, ids, context=None):
		ir_values = self.pool.get('ir.values')
		
		config = self.browse(cr, uid, ids[0], context)
		ir_values.set_default(cr, uid, 'website.seo', 'wk_seo_website_meta_title_size',
			config.wk_seo_website_meta_title_size > 0 and config.wk_seo_website_meta_title_size or 70)
		ir_values.set_default(cr, uid, 'website.seo', 'wk_seo_website_meta_description_size',
			config.wk_seo_website_meta_description_size > 0 and config.wk_seo_website_meta_description_size or 165)
		ir_values.set_default(cr, uid, 'website.seo', 'wk_seo_website_meta_keywords_size',
			config.wk_seo_website_meta_keywords_size > 0 and config.wk_seo_website_meta_keywords_size or 21)
		ir_values.set_default(cr, uid, 'website.seo', 'wk_seo_website_meta_keywords_number',
			config.wk_seo_website_meta_keywords_number > 0 and config.wk_seo_website_meta_keywords_number or 27)
		return True