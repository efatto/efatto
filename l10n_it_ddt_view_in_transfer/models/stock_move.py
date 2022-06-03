# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields

class StockMove(models.Model):
    _inherit = 'stock.move'

    package_ids = fields.Many2many(
        related='picking_id.ddt_ids',
        store=True,
        string='DdT',
    )