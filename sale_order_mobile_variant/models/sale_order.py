# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp


class SaleOrder(models.Model):
    _inherit = ['sale.order', "product.configurator"]
    _name = "sale.order"

    product_template_id = fields.Many2one('product.template')
    product_template_image = fields.Binary(
        related='product_template_id.image_medium')
    product_attribute_line_id = fields.Many2one(
        'product.attribute.line',
        domain="[('product_tmpl_id','=',product_template_id)]"
        )
    product_attribute_value_ids = fields.Many2many(
        string='Values',
        related='product_attribute_line_id.value_ids',
        readonly=True)
    product_attribute_value_id = fields.Many2one(
        'product.attribute.value',
        domain="[('id', 'in', product_attribute_value_ids[0][2])]"
    )
    product_attribute_image = fields.Binary(
        related='product_attribute_value_id.image')
    price_unit = fields.Float(string='Price unit',
                              digits_compute=dp.get_precision('Product Price'))
    product = fields.Char()

    @api.onchange('product_template_id')
    def onchange_product(self):
        self.product_attribute_line_id = \
            self.product_attribute_value_id = False

    @api.onchange('product_attribute_line_id')
    def onchange_product_attribute(self):
        self.product_attribute_value_id = False

    @api.onchange('product_attribute_value_id')
    def onchange_product_attribute_value(self):
        for order in self:
            product = self.env['product.product'].search([
                ('product_tmpl_id','=', order.product_template_id.id),
                ('attribute_value_ids','=', order.product_attribute_value_id.id)
            ])
            if len(product) == 1:
                order.product = product.default_code

    @api.multi
    @api.onchange('product_attribute_value_id')
    @api.depends('product_template_id')
    def onchange_price_unit(self):
        self.ensure_one()
        if self.product_template_id:
            price_extra = 0.0
            attribute_id = False
            for attr_line in self.product_attribute_ids:
                price_extra += attr_line.price_extra
                if attr_line.value_id:
                    attribute_id = attr_line.attribute_id
            for attribute_line in self.product_tmpl_id.attribute_line_ids:
                if attribute_line.attribute_id == attribute_id:
                    price_extra += attribute_line.price_extra
            self.price_unit = self.pricelist_id.with_context({
                'uom': self.product_template_id.uom_id.id,
                'date': self.date_order,
                'price_extra': price_extra,
            }).template_price_get(
                self.product_template_id.id, 1.0,
                self.partner_id.id)[self.pricelist_id.id]

    @api.multi
    def add_product_in_order(self):
        for order in self:
            order.scan = order.product
