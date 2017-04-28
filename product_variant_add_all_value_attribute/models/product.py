# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.multi
    def product_attribute_add_all(self):
        for template in self:
            for attribute_line in template.attribute_line_ids:
                attribute_line.value_ids = self.env[
                    'product.attribute.value'].search([
                        ('attribute_id', '=', attribute_line.attribute_id.id)])
