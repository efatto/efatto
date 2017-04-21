# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import api, models, fields
import openerp.addons.decimal_precision as dp


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.multi
    def _get_price_extra(self):
        for product in self:
            price_extra = price_attribute = cost_extra = cost_attribute = 0.0
            for variant_id in product.attribute_value_ids:
                for price_id in variant_id.price_ids:
                    if price_id.product_tmpl_id.id == \
                            product.product_tmpl_id.id:
                        price_extra += price_id.price_extra
                        cost_extra += price_id.cost_extra
                # ADD extra price for attribute
                attribute_line_with_child_ids = product.product_tmpl_id.\
                    attribute_line_ids.filtered("attribute_id.child_ids")
                attribute_line_ids = product.product_tmpl_id.\
                    attribute_line_ids - attribute_line_with_child_ids
                if attribute_line_with_child_ids:
                    for attribute_line in attribute_line_with_child_ids:
                        if variant_id.attribute_id in \
                                attribute_line.attribute_id.child_ids:
                            price_attribute = attribute_line.price_extra
                            cost_attribute = attribute_line.cost_extra
                            break
                if not attribute_line_with_child_ids:
                    attribute_line = product.product_tmpl_id.\
                        attribute_line_ids.filtered(lambda r:
                                                    r.attribute_id ==
                                                    variant_id.attribute_id)
                    if attribute_line:
                        price_attribute = attribute_line.price_extra
                        cost_attribute = attribute_line.cost_extra
            price_extra += price_attribute
            product.price_extra = price_extra
            cost_extra += cost_attribute
            product.cost_extra = cost_extra

    price_extra = fields.Float(
        compute=_get_price_extra,
        string='Variant Extra Price',
        help="This is the sum of the extra price of all attributes",
        digits_compute=dp.get_precision('Product Price')
    )
    cost_extra = fields.Float(
        compute=_get_price_extra,
        string='Variant Extra Cost',
        help="This is the sum of the extra cost of all attributes",
        digits_compute=dp.get_precision('Product Price')
    )
    cost_custom = fields.Float(
        string='Custom cost for manual evaluation',
        digits_compute=dp.get_precision('Product Price')
    )

class ProductAttributeLine(models.Model):
    _inherit = "product.attribute.line"

    price_extra = fields.Float(
        'Price Extra', digits_compute=dp.get_precision('Product Price')
    )
    cost_extra = fields.Float(
        'Cost Extra', digits_compute=dp.get_precision('Product Price')
    )


class ProductAttributePrice(models.Model):
    _inherit = "product.attribute.price"

    cost_extra = fields.Float(
        'Cost Extra', digits_compute=dp.get_precision('Product Price')
    )
