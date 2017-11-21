# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class StockDdtType(models.Model):
    _inherit = 'stock.ddt.type'

    type_code = fields.Selection(
        related='picking_type_id.code'
    )
