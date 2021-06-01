# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, api, fields


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    @api.depends('picking_ids.ddt_supplier_number', 'picking_ids.ddt_supplier_date')
    def _get_pickings(self):
        for inv in self.filtered(
                lambda x: x.type in ['in_invoice', 'in_refund']):
            pickings_in_ref = False
            if inv.picking_ids:
                pickings_in_ref = ' - '.join([
                    '_'.join([
                        x.ddt_supplier_number if x.ddt_supplier_number else '',
                        x.ddt_supplier_date.strftime('%d/%m/%Y')
                        if x.ddt_supplier_date else ''
                    ])
                    for x in inv.picking_ids])
            inv.pickings_in_ref = pickings_in_ref

    pickings_in_ref = fields.Char(
        compute=_get_pickings, store=True, index=True)
