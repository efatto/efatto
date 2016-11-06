# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp.osv import osv, fields
from openerp.tools.translate import _
import psycopg2
from openerp import tools


class product_product(osv.osv):
    _inherit = "product.product"

    _columns = {
        'att_image': fields.related(
            'attribute_value_ids', 'image', string="Attribute Image",
            type='binary', store=False),
    }

class product_template(osv.osv):
    _inherit = "product.template"

    def create_variant_ids(self, cr, uid, ids, context=None):
        product_obj = self.pool.get("product.product")
        ctx = context and context.copy() or {}

        if ctx.get("create_product_variant"):
            return None

        ctx.update(active_test=False, create_product_variant=True)

        tmpl_ids = self.browse(cr, uid, ids, context=ctx)
        for tmpl_id in tmpl_ids:

            # list of values combination
            variant_alone = []
            all_variants = []
            for variant_id in tmpl_id.attribute_line_ids:
                if len(variant_id.value_ids) == 1:
                    variant_alone.append(variant_id.value_ids[0])
                # temp_variants = []
                # for variant in all_variants:
                for value_id in variant_id.value_ids:
                    all_variants.append(sorted([int(value_id)]))
                # if temp_variants:
                #     all_variants = temp_variants

            # adding an attribute with only one value should not recreate product
            # write this attribute on every product to make sure we don't lose them
            for variant_id in variant_alone:
                product_ids = []
                for product_id in tmpl_id.product_variant_ids:
                    if variant_id.id not in map(int, product_id.attribute_value_ids):
                        product_ids.append(product_id.id)
                product_obj.write(cr, uid, product_ids, {'attribute_value_ids': [(4, variant_id.id)]}, context=ctx)

            # check product
            variant_ids_to_active = []
            variants_active_ids = []
            variants_inactive = []
            for product_id in tmpl_id.product_variant_ids:
                variants = sorted(map(int,product_id.attribute_value_ids))
                if variants in all_variants:
                    variants_active_ids.append(product_id.id)
                    all_variants.pop(all_variants.index(variants))
                    if not product_id.active:
                        variant_ids_to_active.append(product_id.id)
                else:
                    variants_inactive.append(product_id)
            if variant_ids_to_active:
                product_obj.write(cr, uid, variant_ids_to_active, {'active': True}, context=ctx)

            # create new product
            for variant_ids in all_variants:
                values = {
                    'product_tmpl_id': tmpl_id.id,
                    'attribute_value_ids': [(6, 0, variant_ids)]
                }
                id = product_obj.create(cr, uid, values, context=ctx)
                variants_active_ids.append(id)

            # unlink or inactive product
            for variant_id in map(int,variants_inactive):
                try:
                    with cr.savepoint(), tools.mute_logger('openerp.sql_db'):
                        product_obj.unlink(cr, uid, [variant_id], context=ctx)
                except (psycopg2.Error, osv.except_osv):
                    product_obj.write(cr, uid, [variant_id], {'active': False}, context=ctx)
                    pass
        return True
