# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_bag_id = fields.Many2one(
        'product.product', 'Bag',
        domain=[('is_bag', '=', True)]
    )
    is_bag = fields.Boolean()


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def _get_weight(self):
        for product in self:
            # the weight is the sum of package if exists and product_template
            product.weight = product.product_tmpl_id.product_pack_id.weight + \
                product.product_tmpl_id.weight if \
                product.product_tmpl_id.product_pack_id else \
                product.product_tmpl_id.weight
            product.weight += product.product_tmpl_id.product_bag_id.weight \
                if product.product_tmpl_id.product_bag_id else 0.0

    @api.multi
    def _get_weight_net(self):
        for product in self:
            # the weight is the sum of package if exists and product_template
            product.weight_net = product.product_tmpl_id.product_pack_id. \
                weight_net + product.product_tmpl_id.weight_net if \
                product.product_tmpl_id.product_pack_id else \
                product.product_tmpl_id.weight_net
            product.weight_net += product.product_tmpl_id.product_bag_id.\
                weight_net if product.product_tmpl_id.product_bag_id else 0.0

    weight = fields.Float(compute='_get_weight')
    weight_net = fields.Float(compute='_get_weight_net')
