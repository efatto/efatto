from odoo import models, api, fields, exceptions, _
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def _get_pickings(self):
        for inv in self.filtered(
                lambda x: x.type in ['in_invoice', 'in_refund']):
            pickings_in_ref = False
            if inv.picking_ids:
                pickings_in_ref = ' - '.join([
                    '_'.join([
                        x.in_reference if x.in_reference else '',
                        (
                            datetime.strptime(
                                x.in_date, DEFAULT_SERVER_DATE_FORMAT
                            )).strftime('%d/%m/%Y')
                        if x.in_date else ''
                    ])
                    for x in inv.picking_ids])
            inv.pickings_in_ref = pickings_in_ref

    pickings_in_ref = fields.Char(compute=_get_pickings)
