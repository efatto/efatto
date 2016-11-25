# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class ProductProduct(models.Model):
    _inherit = "product.product"

    att_image = fields.Binary(
        string="Attribute Image",
        related='attribute_value_ids.image',
        store=False)


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    code = fields.Char('Code', required=True)


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    code = fields.Char('Code', required=True)
