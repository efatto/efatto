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
            ('date_to', '>=', invoice.date),
            ('company_id', '=', invoice.company_id.id),
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

    @api.multi
    def _check_duplicate_supplier_reference(self):
        for invoice in self:
            # refuse to validate a vendor bill/credit note if there already exists one
            # with the same reference for the same partner,
            # because it's probably a double encoding of the same bill/credit note
            # ### Whith reference of year ###
            if invoice.type in ('in_invoice', 'in_refund') and invoice.reference:
                first_year_date = invoice.date_invoice and invoice.date_invoice.replace(
                    month=1, day=1) or fields.Date.today().replace(month=1, day=1)
                last_year_date = first_year_date.replace(month=12, day=31)
                if self.search([
                    ('date_invoice', '>=', first_year_date),
                    ('date_invoice', '<=', last_year_date),
                    ('type', '=', invoice.type),
                    ('reference', '=', invoice.reference),
                    ('company_id', '=', invoice.company_id.id),
                    ('commercial_partner_id', '=', invoice.commercial_partner_id.id),
                        ('id', '!=', invoice.id)]):
                    raise UserError(_(
                        "Duplicated vendor reference detected. You probably encoded "
                        "twice the same vendor bill/credit note."))
