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
        if not self.product_id and self.product_tmpl_id:
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
                total_price = self.product_tmpl_id.list_price + price_extra
                if total_price != 0.0:
                    discount = (total_price - price_unit) / total_price * 100.0
                    price_unit = total_price
            self.price_unit = price_unit
            self.discount = discount

    @api.multi
    def update_price_unit(self):
        self.ensure_one()
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
                total_price = self.product_tmpl_id.list_price + price_extra
                if total_price != 0.0:
                    discount = (total_price - price_unit) / total_price * 100.0
                    price_unit = total_price
            self.price_unit = price_unit
            self.discount = discount


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def recalculate_prices(self):
        for line in self.order_line:
            line.update_price_unit()
        #super(SaleOrder, self).recalculate_prices()