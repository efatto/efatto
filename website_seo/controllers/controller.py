# -*- coding: utf-8 -*-
#################################################################################
#Add Comments About Your Order
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################
from openerp.addons.web import http
from openerp.http import request 
from openerp.tools.translate import _
from openerp.addons.website_sale.controllers.main import website_sale 
from openerp.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)
import re
class website_sale(website_sale):
    @http.route(['/shop',
        '/shop/page/<int:page>',
        '/shop/category/<model("product.public.category"):category>',
        '/shop/category/<model("product.public.category"):category>/page/<int:page>'
    ], type='http', auth="public", website=True)
    def shop(self, page=0, category=None,brand=None, search='', **post):
        response=super(website_sale,self).shop(page, category, search)
        category_obj = request.env['product.public.category'].sudo().search([('parent_id', '=', False)])
        if category and category.website_meta_title:
            response.qcontext.update({'main_object': category})
            if page:
                category.website_meta_title +='|page-'+str(page)
            else :
               
              
                pk = re.sub(r'(?<=page).*', '',category.website_meta_title)
                category.website_meta_title  = pk.rstrip('|page')
                



        return  response





  



        
		

		

	


	
	





   		
    

	


	
 		