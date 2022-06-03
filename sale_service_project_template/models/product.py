# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    project_template_id = fields.Many2one(
        comodel_name='project.project',
        string='Template Project',
        )


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.multi
    def need_procurement(self):
        for product in self:
            if product.type == 'service' and product.project_template_id:
                return True
        return super(ProductProduct, self).need_procurement()