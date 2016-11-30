# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_pack_id = fields.Many2one(
        'product.template', 'Pack',
        domain=[('is_pack','=',True)]
    )
    is_pack = fields.Boolean()

    @api.onchange('product_pack_id')
    def onchange_pack(self):
        for product in self:
            product.volume = product.product_pack_id.volume
            product.weight = product.weight_net + \
                             product.product_pack_id.weight_net

    @api.onchange('weight_net')
    @api.depends('product_pack_id')
    def onchange_weight_net(self):
        for product in self:
            product.weight = product.weight_net + \
                             product.product_pack_id.weight_net
