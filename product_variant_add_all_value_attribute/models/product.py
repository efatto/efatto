# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api


class ProductAttributeLine(models.Model):
    _inherit = "product.attribute.line"

    @api.onchange('attribute_id')
    def attribute_change(self):
        self.value_ids = self.env[
            'product.attribute.value'].search([
                ('attribute_id', '=', self.attribute_id.id)])
