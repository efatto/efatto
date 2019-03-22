# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import Warning as UserError
from odoo.tools.translate import _


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    complex_discount = fields.Char(
        'Complex Discount', size=32,
        help='E.g.: 15.5+5, or 50+10+3.5')

    @api.onchange('complex_discount', 'discount')
    def onchange_sconti(self):
        net = 0.0
        if self.complex_discount:
            complex_discount = self.complex_discount.replace(
                '%', '').replace(',', '.').replace('-', '+').replace(' ', '+')
            for disc in complex_discount.split('+'):
                try:
                    net = 100 - ((100.00 - net) * (100.00 - float(disc)) / 100)
                except:
                    UserError(_('Bad discount format'))
        else:
            net = self.discount
        self.discount = net
