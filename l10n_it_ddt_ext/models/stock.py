# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, exceptions, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def _get_invoice_vals(self, key, inv_type, journal_id, move):
        values = super(StockPicking, self)._get_invoice_vals(
            key, inv_type, journal_id, move)
        # ----- Force to use account_id from ddt invoice partner
        if self._context.get('ddt_partner_id', False):
            partner_id = self.env['res.partner'].browse(
                self._context['ddt_partner_id']
            )
            if partner_id:
                if inv_type in ('out_invoice', 'out_refund'):
                    values['account_id'] = partner_id.\
                        property_account_receivable.id
                else:
                    values['account_id'] = partner_id. \
                        property_account_payable.id
            partner_shipping_id = move.package_ids.mapped(
                'partner_shipping_id')
            if partner_shipping_id != partner_id:
                values['address_shipping_id'] = partner_shipping_id.id
        return values
