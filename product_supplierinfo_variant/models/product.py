# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, fields


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    attribute_id = fields.Many2one(
        'product.attribute', 'Attribute',
    )
