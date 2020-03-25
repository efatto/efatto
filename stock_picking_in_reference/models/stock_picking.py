# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, fields, exceptions


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    in_reference = fields.Char()
    in_date = fields.Date()
