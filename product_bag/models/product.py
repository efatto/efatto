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

    @api.onchange('product_bag_id','product_pack_id')
    def onchange_bag(self):
        for product in self:
            product.weight = product.weight_net + \
                             product.product_bag_id.weight_net + \
                             product.product_pack_id.weight_net

    @api.onchange('weight_net')
    @api.depends('product_bag_id','product_pack_id')
    def onchange_weight_net(self):
        for product in self:
            product.weight = product.weight_net + \
                             product.product_bag_id.weight_net + \
                             product.product_pack_id.weight_net
