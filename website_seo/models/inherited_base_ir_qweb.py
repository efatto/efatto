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
from openerp.addons.base.ir.ir_qweb import FieldConverter
import re 
import logging
_logger = logging.getLogger(__name__)
class FieldConverter(FieldConverter):
	def to_html(self, cr, uid, field_name, record, options,
	source_element, t_att, g_att, qweb_context, context=None):		
		result = super(FieldConverter, self).to_html(cr, uid,field_name, record, options,
		source_element, t_att, g_att, qweb_context)		
		try:           
			if field_name == 'image' and options.get('widget')=='image':
				alt_text = record.img_alt_text if record.img_alt_text else record.name              

				result = re.sub('src'," alt = \'"+alt_text+"\' src ",result)
				return result
		except AttributeError:
			pass



		return result