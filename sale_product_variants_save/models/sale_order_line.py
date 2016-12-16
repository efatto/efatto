# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, fields


class SaleOrderLine(models.Model):
    _inherit = ["sale.order.line", "product.configurator"]
    _name = "sale.order.line"

    @api.model
    def create(self, vals):
        res = super(SaleOrderLine, self).create(vals)
        product_obj = self.env['product.product']
        for line in res.filtered(
                lambda x: not x.product_id and x.product_tmpl_id):
            product = product_obj._product_find(
                line.product_tmpl_id, line.product_attribute_ids)
            if not product:
                product = product_obj.create({
                    'product_tmpl_id': line.product_tmpl_id.id,
                    'attribute_value_ids':
                        [(6, 0,
                          line.product_attribute_ids.mapped('value_id').ids)]})
            line.write({'product_id': product.id})
        return res
