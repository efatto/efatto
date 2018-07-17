# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class StockPickingPackagePreparation(models.Model):
    _inherit = 'stock.picking.package.preparation'

    carrier_signature = fields.Binary(string="Carrier's Signature")
    driver_signature = fields.Binary(string="Driver's Signature")
    recipient_signature = fields.Binary(string="Recipient's Signature")
