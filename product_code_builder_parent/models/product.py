# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, exceptions, _


class ProductProduct(models.Model):
    _inherit = "product.product"

    att_image = fields.Binary(
        string="Attribute Image",
        related='attribute_value_ids.image',
        store=False)

    @api.multi
    def _compute_default_code(self):
        for record in self:
            if not record.product_tmpl_id \
                    .attribute_line_ids:
                record.default_code = record.prefix_code
            elif record.auto_default_code:
                record.default_code = record._get_default_code()
            else:
                record.default_code = record.manual_default_code

    @api.multi
    def _inverse_default_code(self):
        for record in self:
            if not record.product_tmpl_id \
                    .attribute_line_ids:
                record.prefix_code = record.default_code
            elif not record.auto_default_code:
                record.manual_default_code = record.default_code
            else:
                raise exceptions.Warning(
                    _('Default can no be set manually as the product '
                      'is configured to have a computed code'))


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    code = fields.Char('Code', required=True)
    parent_id = fields.Many2one('product.attribute')
    child_ids = fields.One2many(
        'product.attribute',
        'parent_id',
        'Child Attributes'
    )
    value_ids = fields.One2many(
        'product.attribute.value',
        'attribute_id',
        'Attribute Values'
    )
    code_in_report = fields.Char('Code in Report')


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    code = fields.Char('Code', required=True)
