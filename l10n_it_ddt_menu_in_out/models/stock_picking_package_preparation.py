# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockDdtType(models.Model):
    _inherit = 'stock.ddt.type'

    type_code = fields.Selection(
        related='picking_type_id.code'
    )
    partner_type = fields.Selection(
        selection=[
            ('customer', 'Customer'),
            ('supplier', 'Supplier'),
            ('internal', 'Internal'),
        ], compute='_get_partner_type', store=True)

    @api.one
    @api.depends('picking_type_id')
    def _get_partner_type(self):
        if self.picking_type_id.default_location_dest_id == \
                self.env.ref('stock.stock_location_suppliers') or \
                self.picking_type_id.default_location_src_id == \
                self.env.ref('stock.stock_location_suppliers'):
            self.partner_type = 'supplier'
        elif self.picking_type_id.default_location_dest_id == \
                self.env.ref('stock.stock_location_customers') or \
                self.picking_type_id.default_location_src_id == \
                self.env.ref('stock.stock_location_customers'):
            self.partner_type = 'customer'
        else:
            self.partner_type = 'internal'
