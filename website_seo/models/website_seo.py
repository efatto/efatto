# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################

from openerp import api, fields , models 
from openerp.exceptions import Warning
from openerp.exceptions import except_orm, AccessError, MissingError, ValidationError
from openerp.tools.translate import _
import re 
from openerp.addons.base.ir.ir_qweb import FieldConverter
import logging
_logger = logging.getLogger(__name__)

class FieldConverter(FieldConverter):
	def to_html(self, cr, uid, field_name, record, options,
				source_element, t_att, g_att, qweb_context, context=None):
		
		result = super(FieldConverter, self).to_html(
			cr, uid, field_name, record, options,
			source_element, t_att, g_att, qweb_context, context=context)	
		if options.get("widget",False) and options['widget']=='image':
			result = re.sub('src'," alt = \'"+record.name+"\' src ",result)
		else:
			pass
		return result


seo_product_meta_title_list , seo_category_meta_title_list= ['name','categ_id','description',"description_sale",'ean13','default_code', 'company_id'] , ['categ_name','categ_parent_id','category_description']
seo_product_meta_description_list , seo_category_meta_description_list= ['name','categ_id','description', 'description_sale','ean13','default_code', 'company_id'],['categ_name','categ_parent_id','category_description']
seo_product_meta_keyword_list , seo_category_meta_keyword_list = ['name','categ_id','description', 'description_sale','ean13','default_code', 'company_id'],['categ_name','categ_parent_id','category_description']
############# -------------------- beginning of inherited product_template --------------------########################
class product_template(models.Model):
	_inherit = 'product.template'
	seo_auto_update = fields.Boolean(string = 'Auto update', default = 1)
product_template()
############## --------------- beginning of product_public_category-------------------------##########################
class product_public_category(models.Model):    
	_name = 'product.public.category'
	_inherit = ['product.public.category',"website.seo.metadata"]
	seo_auto_update = fields.Boolean(string = 'Auto update', default = 1)
	category_description = fields.Text(string = "Description (About this category)")
product_public_category()
##############-------------- beginning of WebsiteSeoAttribute-------------------------------###################
class WebsiteSeoAttribute(models.Model):
	_name  = "website.seo.attribute"
	_description = 	"""This Class provide the attribute to WebsiteSeo using Many2many relation! """
	_order = 'name'
	def _get_models(self):
		"""internal methods which use to map  the  selected model_name with  website_seo """
		return [('product','Product'),('category','Public Category')]
	name = fields.Char('Name',required=True)
	reference = fields.Selection([('title','Title'),('description','Description'),('keyword','Keyword')],string='Reference',required=True)
	model_name = fields.Selection(_get_models,string='Models',required=True)
	code = fields.Char('Technical Name',required =True)
WebsiteSeoAttribute()
############### --------------beginning of WebsiteSeo--------------------#################################
class WebsiteSeo(models.Model):

	_name="website.seo"
	_description = 	"""
						This is the main class of this module WebsiteSeo !.
						This Class have to methods :
						add_virtual_product AND remove_virtual_product
					"""

	def _get_models(self):
		"""internal methods which fill  selection  field model_name in the form view  """
		return [('product','Product'),('category','Public Category')]

	@api.depends('website_seo_meta_title_ids')
	def _compute_seo_title(self):
		for record in self:
			record.website_meta_title = (" "+str(record.multi_attribute_seperator)+" ").join('{'+str(rec.name)+"}" for rec in record.website_seo_meta_title_ids)

	@api.depends('website_seo_meta_description_ids')
	def _compute_seo_description(self):
		for record in self:
			record.website_meta_description = (" "+str(record.multi_attribute_seperator)+" ").join('{'+str(rec.name)+"}" for rec in record.website_seo_meta_description_ids)

	@api.depends('website_seo_meta_keyword_ids')
	def _compute_seo_keyword(self):
		for record in self:
			record.website_meta_keyword = ', '.join('{'+str(rec.name)+"}" for rec in record.website_seo_meta_keyword_ids)

	def _get_seo_config_values(self):
		seo_config_values_list_tuples = self.env['ir.values'].get_defaults('website.seo')
		seo_config_values = {}
		for item in seo_config_values_list_tuples:
			seo_config_values.update({item[1]:item[2]})
		return seo_config_values

	name = fields.Char("Name" , default = "Website SEO")
	model_name = fields.Selection(_get_models,string='SEO Meta Configuration for',required=True, default = 'product')
	
	website_seo_meta_title_ids = fields.Many2many("website.seo.attribute",  "website_seo_title_seo_attribute_relation", "wk_website_seo_title","wk_website_seo_attribute_title",  "Add Title")
	website_seo_meta_description_ids = fields.Many2many(comodel_name = "website.seo.attribute", relation = "website_seo_description_seo_attribute_relation", column1 = "wk_website_seo_description",column2 = "wk_website_seo_attribute_description", string="Add Description" )
	website_seo_meta_keyword_ids = fields.Many2many(comodel_name = "website.seo.attribute", relation = "website_seo_keyword_seo_attribute_relation", column1 = "wk_website_seo_keywords",column2 = "wk_website_seo_attribute_keyword", string="Add Keywords" )
	
	multi_value_seperator = fields.Char("Multi Value Separator", required = 1)
	multi_attribute_seperator = fields.Char("Multi Attribute Separator", required = 1)

	website_meta_title = fields.Char("Meta Title",compute = _compute_seo_title) 
	website_meta_description = fields.Char("Meta Description",compute = _compute_seo_description)
	website_meta_keyword =  fields.Char("Meta Keywords", compute = _compute_seo_keyword)
		
	_sql_constraints = [('unique_name', 'unique(model_name)', 'A single seo can be configure for a model!')]
	
	def _get_seo_substring(self,substr,multi_value_seperator=','): 
		return multi_value_seperator.join(x for x in substr.split(" ") if x) if substr else ''

	def _get_wrap_arrtribute_name(self, attribute, model_name_obj,multi_value_seperator='-',multi_attribute_seperator='|'):
		result = ''
		if attribute =='name':
			result = self._get_seo_substring(model_name_obj.name,multi_value_seperator)
		elif attribute =='categ_id': 
			result = self._get_seo_substring(model_name_obj.categ_id.name,multi_value_seperator)
		elif attribute =='description_sale':  
			result = self._get_seo_substring(model_name_obj.description_sale,multi_value_seperator)
		elif attribute =='ean13':  
			result = self._get_seo_substring(model_name_obj.ean13,multi_value_seperator)
		elif attribute =='description':  
			result = self._get_seo_substring(model_name_obj.description,multi_value_seperator)
		elif attribute == 'company_id':
			result = self._get_seo_substring(model_name_obj.company_id.name,multi_value_seperator)
		elif attribute == 'default_code':
			result = self._get_seo_substring(model_name_obj.default_code,multi_value_seperator)
		elif attribute == 'categ_name':		
			result = self._get_seo_substring(model_name_obj.name,multi_value_seperator)
		elif attribute == 'categ_parent_id':
			result = self._get_seo_substring(model_name_obj.parent_id.name,multi_value_seperator)
		elif attribute == 'category_description':
			result = self._get_seo_substring(model_name_obj.category_description,multi_value_seperator)

		if result:
			result += multi_attribute_seperator 
		return result


	@api.one 
	def  _set_meta_info(self, model_name_obj, meta_title_attribute, meta_description_attribute, meta_keyword_attribute):	
		seo_config_values = self._get_seo_config_values()
		attribute_separator = " " + self.multi_attribute_seperator + " "
		seo_title , titles_max_len= '', seo_config_values.get('wk_seo_website_meta_title_size',70)
		seo_description ,descriptions_max_len  =  '', seo_config_values.get('wk_seo_website_meta_description_size',165)
		seo_keyword ,keyword_max_len, keyword_max_num  =  '', seo_config_values.get('wk_seo_website_meta_keywords_size',10), seo_config_values.get('wk_seo_website_meta_keywords_number',27)

		for attribute in meta_title_attribute:			
			seo_title += self._get_wrap_arrtribute_name(attribute.code ,model_name_obj, self.multi_value_seperator, attribute_separator)	
		seo_title = seo_title[:-len(attribute_separator)].strip()
		
		model_name_obj.website_meta_title = seo_title if len(seo_title) < titles_max_len else seo_title[:titles_max_len]
		for attribute in meta_description_attribute:			
			seo_description += self._get_wrap_arrtribute_name(attribute.code ,model_name_obj, self.multi_value_seperator,attribute_separator)
		seo_description = seo_description[:-len(attribute_separator)].strip()		
		model_name_obj.website_meta_description = seo_description if len(seo_description) <descriptions_max_len else seo_description[:descriptions_max_len]
		for attribute in meta_keyword_attribute:			
			seo_keyword += self._get_wrap_arrtribute_name(attribute.code ,model_name_obj,'-',', ')
		seo_keyword = seo_keyword[:-1].strip()
		temp_seo_words =re.findall(r'[^,]+', seo_keyword if len(seo_keyword) <keyword_max_len else seo_keyword[:keyword_max_len])
		model_name_obj.website_meta_keywords = ",".join(temp_seo_words) if len(temp_seo_words)<keyword_max_num else ",".join(temp_seo_words[:keyword_max_num])
		
		return True
		

	def _seo_genrated(self,cr,uid,ids,message,context=None):
		if context is None:
			context = {}
		partial_id = self.pool.get('wk.wizard.message').create(cr, uid, {'text':message}, context=context)
		return {
						'name':"SEO information Updated !",
						'view_mode': 'form',
						'view_id': False,
						'view_type': 'form',
						'res_model': 'wk.wizard.message',
						'res_id': partial_id,
						'type': 'ir.actions.act_window',
						'nodestroy': True,
						'target': 'new',
						'domain': '[]',
						'context': context
					}


	@api.multi
	def save_meta_info(self):
		titles , descriptions, keyword = self.website_meta_title , self.website_meta_description, self.website_meta_keyword
		meta_title_attribute = set([i.code for i in self.website_seo_meta_title_ids])
		meta_description_attribute = set([i.code for i in self.website_seo_meta_description_ids])	
		meta_keyword_attribute	= set([i.code for i in self.website_seo_meta_keyword_ids])	
		
		if self.model_name == 'product':	
			condition = meta_title_attribute <= set(seo_product_meta_title_list)  and meta_description_attribute <= set(seo_product_meta_description_list) and meta_keyword_attribute <= set(seo_product_meta_keyword_list)
			
			if not condition :
				raise ValidationError("Some Attribute are not valid for product model !")
			else:
				products = self.env['product.template'].search([('seo_auto_update','=',True)])
				for product in products:					
					self._set_meta_info( product ,  self.website_seo_meta_title_ids , self.website_seo_meta_description_ids , self.website_seo_meta_keyword_ids)		
				message=_("<h2>The SEO information for  products has been Updated successfully...!</h2><h4>Total %d products items is now influence  by this SEO Updation.</h4><h4>NOTE: SEO information for those products will not update in which you ticked  off \"Auto Update\". </h4> "%(len(products)))				
				return self._seo_genrated(message)
		elif self.model_name == 'category':	
			condition =  meta_title_attribute <= set(seo_category_meta_title_list) and meta_description_attribute <= set(seo_category_meta_description_list) and meta_keyword_attribute <= set(seo_category_meta_keyword_list) 
			
			if not condition:
				raise ValidationError("Some Attribute are not valid for category model !")			
			else:
				categorys = self.env['product.public.category'].search([('seo_auto_update','=',True)])
				for category in categorys:
					self._set_meta_info( category ,self.website_seo_meta_title_ids ,self.website_seo_meta_description_ids, self.website_seo_meta_keyword_ids)		
				message=_("<h2>The SEO information for  Categories has been Updated successfully...!</h2><h4>Total %d categories  are influence  by this SEO Updation.</h4><h4>NOTE: SEO information for those Categories will not update where you unchecked   \"Auto Update\". </h4>"%(len(categorys)))	
				return self._seo_genrated(message)
WebsiteSeo()