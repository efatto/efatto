# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_pack_id = fields.Many2one(
        'product.product', 'Pack',
        domain=[('is_pack', '=', True)]
    )
    is_pack = fields.Boolean()

    @api.onchange('product_pack_id')
    def onchange_pack(self):
        for product in self:
            product.weight = product.weight_net + \
                product.product_pack_id.weight_net

    @api.onchange('weight_net')
    @api.depends('product_pack_id')
    def onchange_weight_net(self):
        for product in self:
            product.weight = product.weight_net + \
                product.product_pack_id.weight_net


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def _get_volume(self):
        for product in self:
            # the package is esternal of all packaging so volume is only that
            product.volume = product.product_tmpl_id.product_pack_id.volume if\
                product.product_tmpl_id.product_pack_id else \
                product.product_tmpl_id.volume

    volume = fields.Float(
        compute='_get_volume'
    )