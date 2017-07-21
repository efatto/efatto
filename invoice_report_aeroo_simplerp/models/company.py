# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    logo_width = fields.Float(
        string='Width of logo (cm)',
        help='Width will be proportioned to max 8 cm',
        default=4)
    logo_heigth = fields.Float(
        string='Height of logo (cm)',
        help='Height will be proportioned to max 3 cm',
        default=1.5)

    @api.onchange('logo_heigth')
    def onchange_logo(self):
        if self.logo_heigth <= 0:
            self.logo_heigth = 1.5
        if self.logo_width <= 0:
            self.logo_width = 4

        if self.logo_heigth > 3 or self.logo_width > 8:
            prop = (self.logo_width * 100.0) / (self.logo_heigth * 100.0)
            height = 8 / prop
            width = 8
            if height > 3:
                height = 3
                width = 3 * prop
            self.logo_heigth = height
            self.logo_width = width
