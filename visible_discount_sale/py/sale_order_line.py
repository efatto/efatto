from openerp import models, fields, api


class sale_order_line(models.Model):
    _inherit = 'sale.order.line'
    
    def product_id_change( self, cr, uid, ids, pricelist, product, qty=0, uom=False, qty_uos=0, uos=False, name='', partner_id=False,
        lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context = None ):
        
        def get_real_price( res_dict, product_id, qty, uom, pricelist ):
            item_obj = self.pool['product.pricelist.item']
            price_type_obj = self.pool['product.price.type']
            product_obj = self.pool['product.product']
            
            field_name = 'list_price'
            if res_dict[pricelist][1] != False :
                item = res_dict[pricelist][1]
                item_base = item_obj.read( cr, uid, [item], ['base'] )[0]['base']
                if item_base > 0:
                    field_name = price_type_obj.browse( cr, uid, item_base ).field
            
            product = product_obj.browse( cr, uid, product_id, context )
            product_read = product_obj.read( cr, uid, product_id, [field_name], context=context )
            if field_name == 'list_price' and product.list_price != product.lst_price:
                field_name = 'lst_price'
                product_read = product_obj.read(cr, uid, product_id,
                                                ['lst_price'], context=context)
            factor = 1.0
            if uom and uom != product.uom_id.id:
                product_uom_obj = self.pool.get( 'product.uom' )
                uom_data = product_uom_obj.browse( cr, uid, product.uom_id.id )
                factor = uom_data.factor
            return product_read[field_name] * factor
        
        pricelist_obj = self.pool['product.pricelist']
        pricelists = pricelist_obj.browse(cr, uid, pricelist, context=context)

        res = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty=qty, uom=uom, qty_uos=qty_uos, uos=uos, 
            name=name, partner_id=partner_id, lang=lang, update_tax=update_tax, date_order=date_order, packaging=packaging,
             fiscal_position=fiscal_position, flag=flag, context= context)
        
        if not pricelists:
            return res
        if not pricelists.visible_discount:
            return res
        
        if not product:
            return res
        
        price_unit = res['value']['price_unit']
        discount_new = 0.0

        if res['value'].get( 'price_unit', False ):
            price = res['value']['price_unit']
            list_price = pricelists.with_context({'uom': uom, 'date': date_order }).price_rule_get(product, qty or 1.0, partner_id)
            pricelst = pricelists.read(['visible_discount'])
            new_list_price = get_real_price( list_price, product, qty, uom, pricelist )

            if len( pricelst ) > 0 and pricelst[0]['visible_discount'] and list_price[pricelist][0] != 0 and new_list_price != 0:
                discount = ( new_list_price - price ) / new_list_price * 100
                price_unit = new_list_price
                discount_new = discount
        
        res['value'].update( {
             'product_id':product,
             'price_unit' : price_unit,
             'discount' : discount_new,
             } )
        return res