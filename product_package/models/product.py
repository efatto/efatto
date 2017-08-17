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

    @api.multi
    def _get_volume(self):
        for product in self:
            # the package is external of all packaging so volume is only that
            product.volume = product.product_tmpl_id.product_pack_id.volume if\
                product.product_tmpl_id.product_pack_id else \
                product.product_tmpl_id.volume

    @api.multi
    def _get_weight(self):
        for product in self:
            # the weight is the sum of package if exists and product_template
            product.weight = product.product_tmpl_id.product_pack_id.weight + \
                product.product_tmpl_id.weight if \
                product.product_tmpl_id.product_pack_id else \
                product.product_tmpl_id.weight

    @api.multi
    def _get_weight_net(self):
        for product in self:
            # the weight is the sum of package if exists and product_template
            product.weight_net = product.product_tmpl_id.product_pack_id.\
                weight_net + product.product_tmpl_id.weight_net if \
                product.product_tmpl_id.product_pack_id else \
                product.product_tmpl_id.weight_net

    volume = fields.Float(compute='_get_volume',
                          digits_compute=dp.get_precision('Stock Volume'),
                          digits=dp.get_precision('Stock Volume'))
    weight = fields.Float(compute='_get_weight',
                          digits_compute=dp.get_precision('Stock Weight'),
                          digits=dp.get_precision('Stock Weight'))
    weight_net = fields.Float(compute='_get_weight_net',
                              digits_compute=dp.get_precision('Stock Weight'),
                              digits=dp.get_precision('Stock Weight'))
