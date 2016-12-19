# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_transport = fields.Boolean()
    is_other = fields.Boolean()
    is_contribution = fields.Boolean()
    is_discount = fields.Boolean()
