# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    parent_id = fields.Many2one('product.attribute', 'Parent attribute')
