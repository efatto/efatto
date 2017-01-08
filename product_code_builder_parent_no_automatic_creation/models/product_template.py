# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api
from openerp.tools import config


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.multi
    def create_variant_ids(self):
        if (config['test_enable'] and
                not self.env.context.get('check_variant_creation')):
            return super(ProductTemplate, self).create_variant_ids()
        for tmpl in self:
            if ((tmpl.no_create_variants == 'empty' and
                     not tmpl.categ_id.no_create_variants) or
                        tmpl.no_create_variants == 'no'):
                super(ProductTemplate, tmpl).create_variant_ids()
        return True