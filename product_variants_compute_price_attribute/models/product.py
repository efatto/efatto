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
        # result = dict.fromkeys(ids, False)
        for product in self:
            price_extra = 0.0
            for variant_id in product.attribute_value_ids:
                for price_id in variant_id.price_ids:
                    if price_id.product_tmpl_id.id == product.product_tmpl_id.id:
                        price_extra += price_id.price_extra
                        # ADD extra price for attribute
                        attribute_line = product.product_tmpl_id.\
                            attribute_line_ids.filtered(lambda r:
                                                        r.attribute_id ==
                                                        price_id.attribute_id)
                        if attribute_line:
                            price_extra += attribute_line.price_extra
            product.price_extra = price_extra

    price_extra = fields.Float(
        compute=_get_price_extra,
        string='Variant Extra Price',
        help="This is the sum of the extra price of all attributes",
        digits_compute=dp.get_precision('Product Price')
    )


class ProductAttributeLine(models.Model):
    _inherit = "product.attribute.line"

    price_extra = fields.Float(
            'Price Extra', digits_compute=dp.get_precision('Product Price')
    )
