# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class ProductProduct(models.Model):
    _inherit = "product.product"

    att_image = fields.Binary(
        string="Attribute Image",
        related='attribute_value_ids.image',
        store=False)


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    code = fields.Char('Code', required=True)
    parent_id = fields.Many2one('product.attribute')
    child_ids = fields.One2many(
        'product.attribute',
        'parent_id',
        'Child Attributes'
    )
    value_ids = fields.One2many(
        'product.attribute.value',
        'attribute_id',
        'Attribute Values'
    )


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    code = fields.Char('Code', required=True)
