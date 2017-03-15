# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, _


class StockInvoiceOnshipping(models.TransientModel):
    _inherit = "stock.invoice.onshipping"

    @api.multi
    def create_invoice(self):
        picking_obj = self.env['stock.picking']
        res = super(StockInvoiceOnshipping, self).create_invoice()
        active_ids = self._context.get('active_ids', [])
        for picking in picking_obj.browse(active_ids):
            for ddt in picking.ddt_ids:
                for invoice in self.env['account.invoice'].browse(res):
                    if ddt.partner_id == invoice.partner_id and \
                            picking.name in invoice.origin:
                        ddt.invoice_id = invoice.id
        return res
