# Copyright 2015-2019 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import datetime

from odoo import models, api, fields, _
from odoo.exceptions import UserError
from odoo.tools.misc import format_date


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.model
    def _prepare_later_invoices_domain(self, invoice):
        domain = [
            ('journal_id', '=', invoice.journal_id.id),
            ('date', '>', invoice.date),
            ('number', '<', invoice.number),
        ]
        # check until last date of registration year date_range only
        registration_fy = self.env['account.fiscal.year'].search([
            ('date_from', '<=', invoice.date),
            ('date_to', '>=', invoice.date)
        ])
        if registration_fy:
            domain.append(('date', '<=', registration_fy.date_to))
        # check on same type if sequence for refund is separate
        if invoice.journal_id.refund_sequence:
            domain.append(('type', '=', invoice.type))
        return domain

    @api.multi
    def action_move_create(self):
        previously_validated = self.filtered(lambda x: x.move_name)
        res = super(AccountInvoice, self).action_move_create()
        for inv in self:
            if not inv.journal_id.check_chronology:
                continue

            if inv.type in ('in_invoice', 'in_refund'):
                if inv.date_invoice and inv.date and inv.date_invoice > inv.date:
                    raise UserError(
                        _("Supplier invoice date %s cannot be later than "
                          "the date %s of registration!" % (
                            inv.date_invoice, inv.date)
                          )
                    )
            if inv not in previously_validated:
                invoices = self.search(
                    self._prepare_later_invoices_domain(inv),
                    order='date desc', limit=1)
                if invoices:
                    date_invoice_format = datetime.datetime(
                        year=invoices[0].date.year,
                        month=invoices[0].date.month,
                        day=invoices[0].date.day,
                    )
                    date_invoice_tz = format_date(
                        self.env, fields.Date.context_today(
                            self, date_invoice_format))
                    raise UserError(_(
                        "Chronology Error. Post the invoice with an equal "
                        "or greater date than {date_invoice}.").format(
                        date_invoice=date_invoice_tz))
        return res
