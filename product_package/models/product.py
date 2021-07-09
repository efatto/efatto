# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, fields
import openerp.addons.decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_pack_id = fields.Many2one(
        'product.product', 'Pack',
        domain=[('is_pack', '=', True)]
    )
    is_pack = fields.Boolean()


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.depends('product_tmpl_id.product_pack_id',
                 'product_tmpl_id.product_pack_id.volume',
                 'product_tmpl_id.volume')
    def _get_volume(self):
        for product in self:
            # the package is external of all packaging so volume is only that
            product.volume = product.product_tmpl_id.product_pack_id.volume if\
                product.product_tmpl_id.product_pack_id else \
                product.product_tmpl_id.volume

    @api.depends('product_tmpl_id.product_pack_id',
                 'product_tmpl_id.weight_net',
                 'product_tmpl_id.product_pack_id.weight_net')
    def _get_weight(self):
        for product in self:
            # gross weight is the sum of net weight of package if exists and
            # net weight of product_template
            product.weight = product.product_tmpl_id.product_pack_id.weight_net + \
                product.product_tmpl_id.weight_net if \
                product.product_tmpl_id.product_pack_id else \
                product.product_tmpl_id.weight_net

    @api.depends('product_tmpl_id.weight_net')
    def _get_weight_net(self):
        for product in self:
            # net weight is the same of the product_template
            product.weight_net = product.product_tmpl_id.weight_net

    volume = fields.Float(compute='_get_volume',
                          digits_compute=dp.get_precision('Stock Volume'),
                          digits=dp.get_precision('Stock Volume'))
    weight = fields.Float(compute='_get_weight',
                          digits_compute=dp.get_precision('Stock Weight'),
                          digits=dp.get_precision('Stock Weight'))
    weight_net = fields.Float(compute='_get_weight_net',
                              digits_compute=dp.get_precision('Stock Weight'),
                              digits=dp.get_precision('Stock Weight'))
