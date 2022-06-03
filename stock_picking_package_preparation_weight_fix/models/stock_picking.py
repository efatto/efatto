# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, fields
import openerp.addons.decimal_precision as dp


class StockPickingPackagePreparation(models.Model):
    _inherit = 'stock.picking.package.preparation'

    weight = fields.Float(
        compute='_compute_weight',
        help="The weight is computed when the preparation "
        "is done.",
        digits_compute=dp.get_precision('Stock Weight'))
    net_weight = fields.Float(
        compute='_compute_weight',
        help="The weight is computed when the "
        "preparation is done.",
        digits_compute=dp.get_precision('Stock Weight'))
    volume = fields.Float(
        compute='_compute_weight',
        help="The volume is computed when the "
        "preparation is done.",
        digits_compute=dp.get_precision('Stock Weight'))
    weight_custom = fields.Float(
        help="Custom weight.",
        digits_compute=dp.get_precision('Stock Weight'))
    net_weight_custom = fields.Float(
        help="Custom net weight.",
        digits_compute=dp.get_precision('Stock Weight'))
    volume_custom = fields.Float(
        help="Custom volume.",
        digits_compute=dp.get_precision('Stock Weight'))
    compute_weight = fields.Boolean(default=True)

    @api.multi
    def _compute_weight(self):
        for sppp in self:
            if sppp.compute_weight:
                sppp.net_weight = sum(
                    l.product_id.weight_net * l.product_uom_qty for l in
                    sppp.line_ids)
                sppp.weight = sum(
                    l.product_id.weight * l.product_uom_qty for l in sppp.line_ids)
                sppp.volume = sum(
                    l.product_id.volume * l.product_uom_qty for l in sppp.line_ids)
            else:
                sppp.net_weight = sppp.net_weight_custom
                sppp.weight = sppp.weight_custom
                sppp.volume = sppp.volume_custom