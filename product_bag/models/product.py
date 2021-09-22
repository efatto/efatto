# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, fields
import openerp.addons.decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_bag_id = fields.Many2one(
        'product.product', 'Bag',
        domain=[('is_bag', '=', True)]
    )
    is_bag = fields.Boolean()


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.depends('product_tmpl_id.product_pack_id.weight_net',
                 'product_tmpl_id.weight_net',
                 'product_tmpl_id.product_pack_id',
                 'product_tmpl_id.product_bag_id.weight_net',
                 'product_tmpl_id.product_bag_id')
    def _get_weight(self):
        for product in self:
            # gross weight is the sum of:
            # - net weight of package if exists
            # - net weight of bag if exists
            # - net weight of product_template
            product.weight = product.product_tmpl_id.weight_net + (
                product.product_tmpl_id.product_pack_id.weight_net if
                product.product_tmpl_id.product_pack_id else
                product.product_tmpl_id.weight_net * 0.3)
            product.weight += product.product_tmpl_id.product_bag_id.weight_net \
                if product.product_tmpl_id.product_bag_id else 0.0

    weight = fields.Float(
        compute='_get_weight',
        digits_compute=dp.get_precision('Stock Weight'),
        digits=dp.get_precision('Stock Weight'))
