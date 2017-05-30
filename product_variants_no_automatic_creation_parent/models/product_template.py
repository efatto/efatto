# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, exceptions, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    def _get_product_attributes_dict(self):
        if not self:
            return []
        self.ensure_one()
        res = []
        for attribute_line in self.attribute_line_ids:
            if attribute_line.attribute_id.child_ids:
                for child in attribute_line.attribute_id.child_ids:
                    res.append({'attribute_id': child.id})
            else:
                res.append({'attribute_id': attribute_line.attribute_id.id})
        return res
