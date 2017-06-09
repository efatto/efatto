# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    sale_partner_invoice_id = fields.Many2one(
        related='sale_id.partner_invoice_id')
    sale_partner_id = fields.Many2one(
        related='sale_id.partner_id')

    @api.multi
    def print_picking(self):
        return self.env['report'].get_action(
            self, 'stock.report_picking')
