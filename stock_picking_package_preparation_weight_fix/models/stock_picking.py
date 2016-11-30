# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, fields


class StockPickingPackagePreparation(models.Model):
    _inherit = 'stock.picking.package.preparation'

    weight = fields.Float(
        compute='_compute_weight',
        help="The weight is computed when the preparation "
        "is done.")
    net_weight = fields.Float(
        compute='_compute_weight',
        help="The weight is computed when the "
        "preparation is done.")
    volume = fields.Float(
        compute='_compute_weight',
        help="The volume is computed when the "
        "preparation is done.")

    @api.multi
    def _compute_weight(self):
        self.net_weight = sum(
            l.product_id.weight_net * l.product_uom_qty for l in self.line_ids)
        self.weight = sum(
            l.product_id.weight * l.product_uom_qty for l in self.line_ids)
        self.volume = sum(
            l.product_id.volume * l.product_uom_qty for l in self.line_ids)
