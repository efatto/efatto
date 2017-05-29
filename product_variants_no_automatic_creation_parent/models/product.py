# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, exceptions, _


class ProductConfigurator(models.AbstractModel):
    _inherit = 'product.configurator'

    @api.multi
    @api.onchange('product_tmpl_id')
    def onchange_product_tmpl_id(self):
        #TODO get child_ids attribute if present, else super()
        # First, empty current list
        self.product_attribute_ids = [
            (2, x.id) for x in self.product_attribute_ids]
        if not self.product_tmpl_id.attribute_line_ids:
            self.product_id = self.product_tmpl_id.product_variant_ids
        else:
            if not self.env.context.get('not_reset_product'):
                self.product_id = False
            attribute_list = []
            for attribute_line in self.product_tmpl_id.attribute_line_ids:
                #changed for parent stuff
                if attribute_line.attribute_id.child_ids:
                    for child in attribute_line.attribute_id.child_ids:
                        attribute_list.append({
                            'attribute_id': child.id,
                            'product_tmpl_id': self.product_tmpl_id.id,
                            'owner_model': self._name,
                            'owner_id': self.id,
                        })
                #end of change
                else:
                    attribute_list.append({
                        'attribute_id': attribute_line.attribute_id.id,
                        'product_tmpl_id': self.product_tmpl_id.id,
                        'owner_model': self._name,
                        'owner_id': self.id,
                    })
            self.product_attribute_ids = [(0, 0, x) for x in attribute_list]
        # Needed because the compute method is not triggered
        self.product_attribute_ids._compute_possible_value_ids()
        # Restrict product possible values to current selection
        domain = [('product_tmpl_id', '=', self.product_tmpl_id.id)]
        return {'domain': {'product_id': domain}}


class ProductConfiguratorAttribute(models.Model):
    _inherit = 'product.configurator.attribute'

    possible_value_ids = fields.Many2many(
        comodel_name='product.attribute.value',
        compute='_compute_possible_value_ids')

    @api.multi
    @api.depends('attribute_id')
    def _compute_possible_value_ids(self):
        for record in self:
            if record.product_tmpl_id.attribute_line_ids.filtered(
                    lambda x: x.attribute_id.child_ids):
                for attribute_line in record.product_tmpl_id.attribute_line_ids:
                    for child in attribute_line.attribute_id.child_ids:
                        if child == record.attribute_id:
                            record.possible_value_ids = child.value_ids.sorted()
                    for attribute in attribute_line.attribute_id:
                        if attribute == record.attribute_id:
                            record.possible_value_ids = attribute.value_ids.sorted()
            else:
                super(ProductConfiguratorAttribute, self
                      )._compute_possible_value_ids()