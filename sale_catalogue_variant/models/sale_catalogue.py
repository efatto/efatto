# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _, exceptions, tools
import openerp.addons.decimal_precision as dp
import re


class SaleCatalogue(models.Model):
    _name = "sale.catalogue"

    def _get_partner_default(self):
        res = False
        if self._context['params'].get('action', False):
            if self._context['params'].get('action') == \
                    self.env['ir.model.data'].get_object_reference(
                        'sale_catalogue_variant',
                        'action_sale_catalogue_variant_form')[1]:
                res = self.env.user.company_id.\
                    sale_mobile_catalogue_partner_default
        return res

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        default=_get_partner_default)
    pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        related='partner_id.property_product_pricelist',
    )
    product_template_id = fields.Many2one('product.template')
    product_template_image = fields.Binary(
        related='product_template_id.image_medium')
    product_attribute_line_id = fields.Many2one(
        'product.attribute.line',
        domain="[('product_tmpl_id','=',product_template_id)]"
        )
    product_attribute_line_stitching_id = fields.Many2one(
        'product.attribute.line',
        domain="[('product_tmpl_id','=',product_template_id)]"
        )
    stitching_value_ids = fields.Many2many(
        string='Values',
        related='product_attribute_line_stitching_id.value_ids',
        readonly=True)
    stitching_value_id = fields.Many2one(
        'product.attribute.value',
        domain="[('id', 'in', stitching_value_ids[0][2])]"
    )
    product_attribute_child_ids = fields.One2many(
        string='Childs',
        related='product_attribute_line_id.attribute_id.child_ids',
        readonly=True)
    product_attribute_child_id = fields.Many2one(
        'product.attribute',
        domain="[('id', 'in', product_attribute_child_ids[0][2])]"
    )
    product_attribute_value_ids = fields.Many2many(
        string='Values',
        related='product_attribute_line_id.value_ids',
        readonly=True)
    product_attribute_value_id = fields.Many2one(
        'product.attribute.value',
        domain="[('id', 'in', product_attribute_value_ids[0][2])]"
    )
    product_attribute_image = fields.Binary(
        related='product_attribute_value_id.image')
    price_unit = fields.Float(string='Price unit',
                              digits_compute=dp.get_precision('Product Price'))
    product = fields.Char()
    scan = fields.Char('Scan QR Code')
    discount = fields.Float()
    net_price = fields.Float()

    @api.onchange('discount')
    def onchange_discount(self):
        if self.discount:
            self.net_price = round(
                self.price_unit * (100.0 - self.discount) / 100.0 + 0.5, 0)

    @api.onchange('scan')
    def _scan(self):
        if self.scan:
            # FIRST check if it is a product template (x letter-number)
            product_template = self.env['product.template'].search(
                [('prefix_code', '=', self.scan.upper())])
            if product_template:
                self._set_product_template(product_template)
                return
            # TWO check if it is a material-color (1 letter 2 number)
            if re.match('[A-Z][0-9][0-9]', self.scan.upper()):
                material = self.scan[0].upper()
                color = self.scan[1:3]
                self._set_material_color(material, color)
                return

            # THREE check stitching (ST + 2 numbers) - only 3 qr types
            if re.match('ST[0-9][0-9]', self.scan.upper()):
                self._get_stitching(self.scan[-2:], code_stitching='ST')
                return

            # THREE check stitching for comb (& + 2 numbers) - only 3 qr types
            if re.match('&&[0-9][0-9]', self.scan.upper()):
                self._get_stitching(self.scan[-2:], code_stitching='&&')
                return

            # FOUR check simple material (2 number + 1 or 2 letter + 2 number)
            if re.match('[0-9]{2}[A-Z]{1,2}[0-9]{2}', self.scan.upper()):
                material = self.scan[:2].upper()
                color = self.scan[2:].upper()
                self._set_material_color(material, color)
                return

            # NO MATCHES FOUND: clean all fields
            self.product_attribute_line_id = \
                self.product_attribute_child_id = \
                self.product_attribute_value_id = \
                self.product_template_id = False

    @api.multi
    def _set_product_template(self, product_template):
        self.product_template_id = product_template
        self.product = product_template.prefix_code
        self.price_unit = 0.0
        self.scan = ''
        # clean all children fields
        self.product_attribute_line_id = \
            self.product_attribute_child_id = \
            self.product_attribute_value_id = \
            False

    @api.multi
    def _set_material_color(self, material, color):
        attribute = self.env['product.attribute'].search(
            [('code', '=', material)])
        # first search if material has parent
        if attribute and attribute.parent_id:
            # it's a child attribute: set in one passage the attribute line
            # from parent of attribute, and the product_attribute_child_id
            for attribute_line in self.product_template_id. \
                    attribute_line_ids:
                product_attribute_child = \
                    attribute_line.attribute_id.child_ids.filtered(
                        lambda x: x.code == material)
                if product_attribute_child:
                    self.product_attribute_child_id = \
                        product_attribute_child
                    self.product_attribute_line_id = self. \
                        product_template_id.attribute_line_ids.filtered(
                        lambda x: x.attribute_id ==
                                  product_attribute_child.parent_id)
                    self.product = self.product_template_id.prefix_code + \
                                   product_attribute_child.code
                    self._get_color(color)
                    self.scan = ''
                    return
        elif attribute and not attribute.parent_id:
            product_attribute_line = self.product_template_id. \
                attribute_line_ids.filtered(
                    lambda x: x.attribute_id.code == material)
            if product_attribute_line:
                self.product_attribute_line_id = product_attribute_line
                self.product = self.product_template_id.prefix_code + \
                    product_attribute_line.attribute_id.code
                self._get_color(color)
                self.scan = ''
                return

    def _get_color(self, color):
        if self.product_attribute_child_id:
            product_attribute_value = self.product_attribute_child_id. \
                value_ids.filtered(lambda x: x.code == color)
        else:
            product_attribute_value = self.product_attribute_line_id.\
                value_ids.filtered(lambda x: x.code == color)
        if product_attribute_value:
            self.product_attribute_value_id = product_attribute_value
            product = False
            # we can search here for product only if not with child variant
            if not self.product_attribute_child_id.parent_id:
                product = self.env['product.product'].search([
                    ('product_tmpl_id', '=', self.product_template_id.id),
                    ('attribute_value_ids', '=',
                     self.product_attribute_value_id.id)
                ])
            if product:
                self.product = product.default_code
            else:
                if self.product_attribute_child_id:
                    self.product = self.product_template_id.prefix_code + \
                        self.product_attribute_child_id.code + \
                        product_attribute_value.code
                else:
                    self.product = self.product_template_id.prefix_code + \
                        self.product_attribute_line_id.attribute_id.code + \
                        product_attribute_value.code
            self.price_unit = self._get_price_unit()
        else:
            self.product_attribute_value_id = False

    def _get_stitching(self, stitching, code_stitching):
        if self.product_attribute_child_id and self.product_attribute_value_id:
            product_attribute_line = self.product_template_id.\
                attribute_line_ids.filtered(
                    lambda x: x.attribute_id.code == code_stitching)
            if product_attribute_line:
                self.product_attribute_line_stitching_id = product_attribute_line
                stitching_id = product_attribute_line.value_ids.filtered(
                    lambda x: x.code == stitching
                )
                if stitching_id:
                    self.stitching_value_id = stitching_id
                    self.product = self.product_template_id.prefix_code + \
                        self.product_attribute_child_id.code + \
                        self.product_attribute_value_id.code + \
                        self.product_attribute_line_stitching_id.attribute_id.code + \
                        stitching_id.code
            else:
                self.product_attribute_line_stitching_id = False

    @api.multi
    def _get_price_unit(self):
        self.ensure_one()
        if self.product_template_id:
            price_extra = 0.0
            attribute_id = False
            for attr_line in self.product_attribute_line_id:
                price_extra += attr_line.price_extra
                # if attr_line.value_id:
                #     attribute_id = attr_line.attribute_id
            for attribute_line in self.product_attribute_value_id:
                # if attribute_line.attribute_id == attribute_id:
                price_extra += attribute_line.price_extra
            return self.pricelist_id.with_context({
                'uom': self.product_template_id.uom_id.id,
                'date': fields.Date.today(),
                'price_extra': price_extra,
            }).template_price_get(
                self.product_template_id.id, 1.0,
                self.partner_id.id)[self.pricelist_id.id]
