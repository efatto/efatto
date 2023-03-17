from odoo import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        super().onchange_partner_id()
        if not self.partner_id or not self.partner_id.ddt_carrier_id:
            self.ddt_carrier_id = False
            return
        if self.partner_id.ddt_carrier_id:
            self.ddt_carrier_id = self.partner_id.ddt_carrier_id
