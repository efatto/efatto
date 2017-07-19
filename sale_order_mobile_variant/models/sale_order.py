# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _, exceptions, tools
import openerp.addons.decimal_precision as dp
import re


class SaleOrder(models.Model):
    _inherit = ['sale.order', "product.configurator"]
    _name = "sale.order"

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
    product_qty = fields.Float(
        string='Q.ty',)
    scan = fields.Char('Scan QR Code')
    is_same_color_stitching = fields.Boolean('Stitching color of material')
    is_white_stitching = fields.Boolean('White Stitching')
    image = fields.Binary('Image')
    image_medium = fields.Binary(
        'Image Medium', compute='_get_image', inverse='_set_image')
    image1 = fields.Binary('Image1')
    image_medium1 = fields.Binary(
        'Image Medium1', compute='_get_image1', inverse='_set_image1')
    image2 = fields.Binary('Image2')
    image_medium2 = fields.Binary(
        'Image Medium2', compute='_get_image2', inverse='_set_image2')

    @api.multi
    def _get_image(self):
        for record in self:
            record.image_medium = record.image

    @api.multi
    def _get_image1(self):
        for record in self:
            record.image_medium1 = record.image1

    @api.multi
    def _get_image2(self):
        for record in self:
            record.image_medium2 = record.image2

    @api.multi
    def _set_image(self):
        for record in self:
            record.image = tools.image_resize_image_big(record.image_medium)

    @api.multi
    def _set_image1(self):
        for record in self:
            record.image1 = tools.image_resize_image_big(record.image_medium1)

    @api.multi
    def _set_image2(self):
        for record in self:
            record.image2 = tools.image_resize_image_big(record.image_medium2)

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

            # THREE check stitching (2 numbers) - only 3 qr types
            if re.match('ST[0-9][0-9]', self.scan.upper()):
                self._get_stitching(self.scan[-2:])
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
                    if self.is_same_color_stitching:
                        self._get_stitching(
                            self.product_attribute_value_id.code)
                        return
                    if self.is_white_stitching:
                        self._get_stitching('05')
                        return
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
                if self.is_same_color_stitching:
                    self._get_stitching(
                        self.product_attribute_value_id.code)
                    return
                if self.is_white_stitching:
                    self._get_stitching('05')
                    return
                return

    def _get_color(self, color):
        if self.product_attribute_child_id:
            product_attribute_value = self.product_attribute_child_id. \
                value_ids.filtered(lambda x: x.code == color)
        else:
            product_attribute_value = self.product_attribute_line_id.\
                value_ids.filtered(lambda x: x.code == color)
        # we can search here for product only if not with child variant
        if product_attribute_value:
            self.product_attribute_value_id = product_attribute_value
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

    def _get_stitching(self, stitching):
        if self.product_attribute_child_id and self.product_attribute_value_id:
            product_attribute_line = self.product_template_id.\
                attribute_line_ids.filtered(
                    lambda x: x.attribute_id.code == 'ST')
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

    @api.onchange('is_same_color_stitching')
    def onchange_is_samecolor_stitching(self):
        if self.product_attribute_value_id and self.is_same_color_stitching:
            self._get_stitching(
                self.product_attribute_value_id.code)

    @api.onchange('is_white_stitching')
    def onchange_is_white_stitching(self):
        if self.product_attribute_value_id and self.is_white_stitching:
            self._get_stitching('05')

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
                'date': self.date_order,
                'price_extra': price_extra,
            }).template_price_get(
                self.product_template_id.id, 1.0,
                self.partner_id.id)[self.pricelist_id.id]

    @api.multi
    def add_product_to_order(self):
        if self.product:
            product_obj = self.env['product.product']

            # check if written manually
            if not self.product_attribute_value_id and not self.product_template_id:
                # search attribute-child type
                child_attributes = re.search(
                    '[A-Z][0-9]{2}ST[0-9]{2}', self.product.upper())
                if child_attributes:
                    product_template = self.env['product.template'].search(
                        [('prefix_code', '=',
                          self.product.upper().split(child_attributes.group(0))[0])])
                    if product_template:
                        self._set_product_template(product_template)
                    self._set_material_color(
                        child_attributes.group(0)[0], child_attributes.group(0)[1:3])
                    self._get_stitching(child_attributes.group(0)[5:7])

                # serch attribute type only
                attributes = re.search(
                    '[0-9]{6}[A-Z][0-9]{2}', self.product.upper())
                if attributes and not child_attributes:
                    product_template = self.env['product.template'].search(
                        [('prefix_code', '=',
                          self.product.upper().split(attributes.group(0))[0])])
                    if product_template:
                        self._set_product_template(product_template)
                    # material-color 10 T35
                    self._set_material_color(
                        attributes.group(0)[0:1], attributes.group(0)[1:4])
                if not self.product_attribute_value_id:
                    raise exceptions.ValidationError(
                        _('Code is not valid!')
                    )

            # then search product - if it is attribute-child
            if self.product_template_id and self.product_attribute_child_id:
                domain = product_obj._build_attributes_domain(
                    self.product_template_id, [
                        {'value_id': self.product_attribute_value_id.id},
                        {'value_id': self.stitching_value_id.id}])
                product_id = product_obj.search(domain[0])
                if not product_id:
                    product_id = product_obj.create({
                        'product_tmpl_id': self.product_template_id.id,
                        'attribute_value_ids':
                            [(6, 0,
                              [self.product_attribute_value_id.id,
                               self.stitching_value_id.id])]
                    })

            # attribute type only
            if self.product_template_id and not self.product_attribute_child_id:
                product_id = product_obj.search([
                    ('product_tmpl_id', '=', self.product_template_id.id),
                    ('attribute_value_ids', '=',
                     self.product_attribute_value_id.id)
                ])
                if not product_id:
                    product_id = product_obj.create({
                        'product_tmpl_id': self.product_template_id.id,
                        'attribute_value_ids':
                            [(6, 0,
                              [self.product_attribute_value_id.id])]
                    })
        if len(product_id) != 1:
            raise exceptions.ValidationError(
                'Found more than 1 product, product template has malformed '
                'variants.'
            )
        price_unit = self._get_price_unit() or 0.0
        if product_id in self.order_line.mapped('product_id'):
            line = self.order_line.filtered(
                lambda r: r.product_id == product_id)
            line.product_uom_qty += self.product_qty if \
                self.product_qty else 1
        else:
            self.order_line.create({
                'order_id': self.id,
                'product_tmpl_id': product_id.product_tmpl_id.id,
                'product_id': product_id.id,
                'name': product_id.name_template,
                'product_uom_qty': self.product_qty if self.product_qty else 1,
                'price_unit': price_unit,
                'product_uom': product_id.product_tmpl_id.uom_id.id,
                'state': 'draft',
                'delay': 0.0,
            })

        # clean fields invisibles
        self.product_template_id = \
            self.product_attribute_line_id = \
            self.product_attribute_line_stitching_id = \
            self.stitching_value_id = \
            self.product_attribute_child_id = \
            self.product_attribute_value_id = \
            False
        self.product = ''
