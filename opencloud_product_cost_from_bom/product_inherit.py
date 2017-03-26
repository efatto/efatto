# -*- coding: utf-8 -*-

import itertools
from lxml import etree

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
import openerp.addons.decimal_precision as dp
from openerp.osv import osv


import sys
import os
import time
from datetime import date,datetime, timedelta

class mrp_bom(models.Model):
    _inherit = 'mrp.bom'

    
    def write(self, cr, uid, ids, vals, context=None):            
	boleana = super(mrp_bom, self).write(cr, uid, ids, vals, context)

	if type(ids) is not list:
            ids=[ids]
			
	for b in self.browse(cr,uid,ids,context):
		ler_funcao=b.product_tmpl_id.standard_price_new
	return boleana

    
    def create(self, cr, uid, vals, context):
        id = super(mrp_bom, self).create(cr, uid, vals, context)
	for b in self.browse(cr,uid,[id],context):
		ler_funcao=b.product_tmpl_id.standard_price_new
        return id

class product_template(models.Model):
    _inherit = 'product.template'
        
    standard_price_new = fields.Float(compute="_get_standard_price", digits_compute=dp.get_precision('Product Price'))
    
    @api.one
    def _get_standard_price(self):
        if self.id:
            self._cr.execute("select id,product_qty from mrp_bom where product_tmpl_id="+str(self.id))
            bom=self._cr.fetchone()
            if bom!=None and bom[0]!=None:
                custo_total=0
                self._cr.execute("select product_id,product_qty from mrp_bom_line where bom_id="+str(bom[0]))
                bom_linhas=self._cr.fetchall()
                for linhas in bom_linhas:
                    p = self.env['product.product'].browse(linhas[0])
                    custo_total+=p.standard_price * linhas[1]
		if bom[1]>1:
			custo_total=custo_total/bom[1]
                self.standard_price_new=custo_total
                res_id= 'product.template,' + str(self.id)
                res_id_sem = 'product.template,%'
                self._cr.execute("select fields_id from ir_property where name='standard_price' and res_id like '"+str(res_id_sem)+"'")
                propriedade_filds=self._cr.fetchone()
                if propriedade_filds!=None and propriedade_filds[0]!=None:
                        self._cr.execute("select id from ir_property where name='standard_price' and res_id='"+str(res_id)+"'")
                        propriedade=self._cr.fetchone()
                        if propriedade!=None and propriedade[0]!=None:
                            self._cr.execute("update ir_property set value_float="+str(custo_total)+" where name='standard_price' and res_id='"+str(res_id)+"'")
                        else:
                            property_vals = {
                                'fields_id': propriedade_filds[0],
                                'value_float': custo_total,
                                'name': 'standard_price',
                                'res_id': res_id,
                                'type': 'float',
                            }
                            propiedade_id_new = self.env['ir.property'].create(property_vals)
            else:
                self.standard_price_new=self.standard_price_new
        else:
            self.standard_price_new=self.standard_price_new
            
class product_product(models.Model):
    _inherit = 'product.product'
        
    standard_price_new = fields.Float(compute="_get_standard_price", digits_compute=dp.get_precision('Product Price'))
    
    @api.one
    def _get_standard_price(self):
        if self.id:
            self._cr.execute("select id,product_qty from mrp_bom where product_tmpl_id="+str(self.product_tmpl_id.id))
            bom=self._cr.fetchone()
            if bom!=None and bom[0]!=None:
                custo_total=0
                self._cr.execute("select product_id,product_qty from mrp_bom_line where bom_id="+str(bom[0]))
                bom_linhas=self._cr.fetchall()
                for linhas in bom_linhas:
                    p = self.env['product.product'].browse(linhas[0])
                    custo_total+=p.standard_price * linhas[1]
		
		if bom[1]>1:
			custo_total=custo_total/bom[1]
                self.standard_price_new=custo_total
                res_id= 'product.template,' + str(self.product_tmpl_id.id)
                res_id_sem= 'product.template,%'
                self._cr.execute("select fields_id from ir_property where name='standard_price' and res_id like '"+str(res_id_sem)+"'")
                propriedade_filds=self._cr.fetchone()
                if propriedade_filds!=None and propriedade_filds[0]!=None:
                        campo=propriedade_filds[0]
                        self._cr.execute("select id from ir_property where name='standard_price' and res_id='"+str(res_id)+"'")
                        propriedade=self._cr.fetchone()
                        if propriedade!=None and propriedade[0]!=None:
                            self._cr.execute("update ir_property set value_float="+str(custo_total)+" where name='standard_price' and res_id='"+str(res_id)+"'")
                        else:
                            property_vals = {
                                'fields_id': propriedade_filds[0],
                                'value_float': custo_total,
                                'name': 'standard_price',
                                'res_id': res_id,
                                'type': 'float',
                            }
                            propiedade_id_new = self.env['ir.property'].create(property_vals)
            else:
                self.standard_price_new=self.standard_price_new
        else:
            self.standard_price_new=self.standard_price_new
                
                
    
    
    
    
    
    
    
