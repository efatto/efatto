# Copyright (c) 2019, Link IT Europe Srl
# @author: Matteo Bilotta <mbilotta@linkeurope.it>

import datetime

from odoo import api, fields, models


class StockDeliveryNoteCreateWizard(models.TransientModel):
    _inherit = 'stock.delivery.note.create.wizard'

    partner_shipping_id = fields.Many2one(compute='_compute_fields')

    @api.onchange('partner_id')
    def _onchange_partner(self):
        pass

    @api.depends('selected_picking_ids')
    def _compute_fields(self):
        super()._compute_fields()
        partners = self.selected_picking_ids.get_partners()
        self.partner_shipping_id = partners[2]
