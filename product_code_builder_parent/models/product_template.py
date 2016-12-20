# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp.osv import osv
import psycopg2
from openerp import tools


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
            all_variants = [[]]

            # START MODIFICATION
            attribute_line_with_child_ids = tmpl_id.attribute_line_ids.\
                filtered("attribute_id.child_ids")
            attribute_line_ids = tmpl_id.attribute_line_ids - \
                                 attribute_line_with_child_ids
            if not attribute_line_with_child_ids:
                for variant_id in tmpl_id.attribute_line_ids:
                    if len(variant_id.value_ids) == 1:
                        variant_alone.append(variant_id.value_ids[0])
            for attribute_line_with_child_id in attribute_line_with_child_ids: # per ogni categoria
                for variant_id in attribute_line_with_child_id.attribute_id.child_ids: # per ogni materiale ['mat','colore','imp']
                    temp_variants = []
                    # for variant in all_variants:
                    for value_id in variant_id.value_ids:#aggiungo pelle e tutti i colori della pelle
                        temp_variants.append(sorted([int(value_id)]))

                    if temp_variants:
                        all_variants += temp_variants
            temp_variants = []
            # aggiungo ad ogni variante pelle/colore l'impuntura (la sequence dell'impuntura dev'essere > 0)
            if attribute_line_ids:
                for standard_variant_id in attribute_line_ids:
                    for value_id in standard_variant_id.value_ids:
                        for variant in all_variants:
                            temp_variants.append(sorted(variant + [int(value_id)]))
            for variant in temp_variants:
                if len(variant) < 2:
                    temp_variants.pop(temp_variants.index(variant))
            if temp_variants:
                all_variants = temp_variants
            # END MODIFICATION

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
