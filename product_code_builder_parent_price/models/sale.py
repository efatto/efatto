# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import api, models, fields


class SaleOrderLine(models.Model):
    _inherit = ["sale.order.line", "product.configurator"]
    _name = "sale.order.line"

    @api.multi
    @api.onchange('product_attribute_ids')
    @api.depends('product_tmpl_id')
    def onchange_price_unit(self):
        self.ensure_one()
        date = self._context.get('date') or fields.Date.context_today(self)
        if self.product_tmpl_id:
            price_extra = discount = 0.0
            attribute_id = False
            for attr_line in self.product_attribute_ids:
                price_extra += attr_line.price_extra
                if attr_line.value_id:
                    attribute_id = attr_line.attribute_id
            for attribute_line in self.product_tmpl_id.attribute_line_ids:
                if attribute_line.attribute_id == attribute_id:
                    price_extra += attribute_line.price_extra
            price_unit = self.order_id.pricelist_id.with_context({
                'uom': self.product_uom.id,
                'date': self.order_id.date_order,
                'price_extra': price_extra,
            }).template_price_get(
                self.product_tmpl_id.id, self.product_uom_qty or 1.0,
                self.order_id.partner_id.id)[self.order_id.pricelist_id.id]
            if self.order_id.pricelist_id.visible_discount:
                # get base rule of pricelist price to get price
                # on which retrieve discount
                # search valid version
                for v in self.order_id.pricelist_id.version_id:
                    if (((v.date_start is False) or (v.date_start <= date)) and
                            ((v.date_end is False) or (v.date_end >= date))):
                        version = v
                        break
                for rule in version.items_id:
                    # check what rule is applicable
                    if rule.min_quantity and self.product_uom_qty < \
                            rule.min_quantity:
                        continue
                    if (rule.product_tmpl_id and
                                self.product_id.id != rule.product_tmpl_id.id):
                        continue
                    if rule.product_id:
                        continue

                    if rule.categ_id:
                        cat = self.product_id.categ_id
                        while cat:
                            if cat.id == rule.categ_id.id:
                                break
                            cat = cat.parent_id
                        if not cat:
                            continue
                    if rule.base == -1:
                        base_price_list_id = rule.base_pricelist_id
                        total_price = base_price_list_id.with_context({
                            'uom': self.product_uom.id,
                            'date': self.order_id.date_order,
                            'price_extra': price_extra,
                        }).template_price_get(
                            self.product_tmpl_id.id, self.product_uom_qty or
                            1.0,
                            self.order_id.partner_id.id)[
                            base_price_list_id.id]
                if total_price == 0.0:
                    total_price = self.product_tmpl_id.list_price + price_extra
                if total_price != 0.0:
                    discount = (total_price - price_unit) / total_price * 100.0
                    price_unit = total_price
            self.price_unit = price_unit
            self.discount = discount

    @api.multi
    def update_price_unit(self):
        self.ensure_one()
        date = self._context.get('date') or fields.Date.context_today(self)
        if self.product_tmpl_id:
            price_extra = discount = total_price = 0.0
            attribute_id = False
            for attr_line in self.product_attribute_ids:
                price_extra += attr_line.price_extra
                if attr_line.value_id:
                    attribute_id = attr_line.attribute_id
            for attribute_line in self.product_tmpl_id.attribute_line_ids:
                if attribute_line.attribute_id == attribute_id:
                    price_extra += attribute_line.price_extra
            price_unit = self.order_id.pricelist_id.with_context({
                'uom': self.product_uom.id,
                'date': self.order_id.date_order,
                'price_extra': price_extra,
            }).template_price_get(
                self.product_tmpl_id.id, self.product_uom_qty or 1.0,
                self.order_id.partner_id.id)[self.order_id.pricelist_id.id]
            if self.order_id.pricelist_id.visible_discount:
                # get base rule of pricelist price to get price
                # on which retrieve discount
                # search valid version
                for v in self.order_id.pricelist_id.version_id:
                    if (((v.date_start is False) or (v.date_start <= date)) and
                            ((v.date_end is False) or (v.date_end >= date))):
                        version = v
                        break
                for rule in version.items_id:
                    # check what rule is applicable
                    if rule.min_quantity and self.product_uom_qty < \
                            rule.min_quantity:
                        continue
                    if (rule.product_tmpl_id and
                                self.product_id.id != rule.product_tmpl_id.id):
                        continue
                    if rule.product_id:
                        continue

                    if rule.categ_id:
                        cat = self.product_id.categ_id
                        while cat:
                            if cat.id == rule.categ_id.id:
                                break
                            cat = cat.parent_id
                        if not cat:
                            continue
                    if rule.base == -1:
                        base_price_list_id = rule.base_pricelist_id
                        total_price = base_price_list_id.with_context({
                            'uom': self.product_uom.id,
                            'date': self.order_id.date_order,
                            'price_extra': price_extra,
                        }).template_price_get(
                            self.product_tmpl_id.id, self.product_uom_qty or
                            1.0,
                            self.order_id.partner_id.id)[
                            base_price_list_id.id]
                if total_price == 0.0:
                    total_price = self.product_tmpl_id.list_price + price_extra
                if total_price != 0.0:
                    discount = (total_price - price_unit) / total_price * 100.0
                    price_unit = total_price
            self.price_unit = price_unit
            self.discount = discount

    @api.cr_uid_ids_context
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
                          uom=False, qty_uos=0, uos=False, name='',
                          partner_id=False,
                          lang=False, update_tax=True, date_order=False,
                          packaging=False, fiscal_position=False, flag=False,
                          context=None):
        def get_real_price(res_dict, product_id, qty, uom, pricelist):
            context_partner = context.copy()
            context_partner.update({'lang': lang, 'partner_id': partner_id})
            product_obj = self.pool['product.product']
            product_id = product_obj.browse(cr, uid, product,
                                            context=context_partner)
            pricelist_id = self.pool['product.pricelist'].browse(cr, uid,
                                                                 pricelist)
            if product:
                price_extra = discount = 0.0
                attribute_id = False
                product_attribute_idss = res['value']['product_attribute_ids']
                for attribute in product_attribute_idss:
                    for attr_line in self.pool[
                        'product.configurator.attribute'].browse(
                            cr, uid, attribute[2]['attribute_id']):
                        price_extra += attr_line.price_extra
                        if attribute[2].get('value_id', False):
                            attribute_id = attribute[2]['attribute_id']
                for attribute_line in product_id.product_tmpl_id.\
                        attribute_line_ids:
                    if attribute_line.attribute_id.id == attribute_id:
                        price_extra += attribute_line.price_extra
                price_unit = pricelist_id.with_context(
                    {'uom': uom,
                     'date': date_order,
                     'price_extra': price_extra}
                ).template_price_get(
                    product_id.product_tmpl_id.id, qty or 1.0,
                    partner_id,
                )[pricelist]
                return price_unit, price_extra

        pricelist_obj = self.pool['product.pricelist']
        pricelists = pricelist_obj.browse(cr, uid, pricelist, context=context)
        product_obj = self.pool['product.product']
        res = super(SaleOrderLine, self).product_id_change(
            cr, uid, ids, pricelist, product, qty=qty, uom=uom,
            qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
            lang=lang, update_tax=update_tax, date_order=date_order,
            packaging=packaging, fiscal_position=fiscal_position,
            flag=flag, context=context)

        if not pricelists:
            return res
        if not pricelists.visible_discount:
            return res

        if not product:
            return res
        product_id = product_obj.browse(
            cr, uid, product)
        price_unit = res['value']['price_unit']
        discount_new = 0.0

        if res['value'].get('price_unit', False):
            price = res['value']['price_unit']
            list_price = pricelists.with_context(
                {'uom': uom, 'date': date_order}).price_rule_get(product,
                                                                 qty or 1.0,
                                                                 partner_id)
            pricelst = pricelists.read(['visible_discount'])
            new_list_price, price_extra = get_real_price(
                list_price, product, qty, uom, pricelist)

            if len(pricelst) > 0 and pricelst[0]['visible_discount'] and \
                    list_price[pricelist][0] != 0 and new_list_price != 0:
                # discount = (new_list_price - price) / new_list_price * 100
                # price_unit = new_list_price
                # discount_new = discount

                # get base rule of pricelist price to get price
                # on which retrieve discount
                # search valid version
                for v in pricelists.version_id:
                    if (((v.date_start is False) or (
                        v.date_start <= date_order)) and
                            ((v.date_end is False) or (
                                    v.date_end >= date_order))):
                        version = v
                        break
                for rule in version.items_id:
                    # check what rule is applicable
                    if rule.min_quantity and self.product_uom_qty < \
                            rule.min_quantity:
                        continue
                    if (rule.product_tmpl_id and
                                product != rule.product_tmpl_id.id):
                        continue
                    if rule.product_id:
                        continue

                    if rule.categ_id:
                        cat = product_id.categ_id
                        while cat:
                            if cat.id == rule.categ_id.id:
                                break
                            cat = cat.parent_id
                        if not cat:
                            continue
                    if rule.base == -1:
                        base_price_list_id = rule.base_pricelist_id
                        total_price = base_price_list_id.with_context({
                            'uom': uom,
                            'date': date_order,
                            'price_extra': price_extra,
                        }).template_price_get(
                            product_id.product_tmpl_id.id,
                            qty or 1.0,
                            partner_id)[
                            base_price_list_id.id]
                if total_price == 0.0:
                    total_price = product_id.product_tmpl_id.list_price + \
                                  price_extra
                if total_price != 0.0:
                    discount_new = (
                       total_price - new_list_price) / total_price * 100.0
                    price_unit = total_price

        res['value'].update({
            'product_id': product,
            'price_unit': price_unit,
            'discount': discount_new,
        })
        return res


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def recalculate_prices(self):
        for line in self.order_line:
            line.update_price_unit()
        #NO super(SaleOrder, self).recalculate_prices()
