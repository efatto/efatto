# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    product_template_id = fields.Many2one('product.template')
    product_template_image = fields.Binary(
        related='product_template_id.image_medium')
    product_attribute_line_id = fields.Many2one(
        'product.attribute.line',
        domain="[('product_tmpl_id','=',product_template_id)]"
        )
    product_attribute_value_id = fields.Many2one(
        'product.attribute.value',
        domain="[('attribute_id','=',product_attribute_line_id.attribute_id)]"
        )
    product_attribute_image = fields.Binary(
        related='product_attribute_value_id.image')
