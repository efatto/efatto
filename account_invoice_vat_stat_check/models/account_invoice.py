# -*- coding: utf-8 -*-

from odoo import models, api, _
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _check_invoice_reference(self):
        for invoice in self:
            date_range_type = self.env['date.range.type'].search(
                [('fiscal_year', '=', True)])
            date_range = self.env['date.range'].search([
                ('date_start', '<=', invoice.date_invoice),
                ('date_end', '>=', invoice.date_invoice),
                ('type_id', '!=', date_range_type.id),
            ])
            if invoice.type in ('in_invoice', 'in_refund') and invoice.reference:
                if self.search(
                        [('type', '=', invoice.type),
                         ('reference', '=', invoice.reference),
                         ('company_id', '=', invoice.company_id.id),
                         ('commercial_partner_id', '=',
                          invoice.commercial_partner_id.id),
                         ('id', '!=', invoice.id),
                         ('date_invoice', '=', invoice.date_invoice)]):
                    raise UserError(_(
                        "Duplicated vendor reference detected. You probably encoded"
                        " twice the same vendor bill/refund."))

            vat_statement = self.env[
                'account.vat.period.end.statement'].search(
                    [('date_range_ids', 'in', date_range.id)])
            if vat_statement:
                if vat_statement[0].state != 'draft':
                    raise UserError(
                        _('Period %s have already a closed vat statement. '
                          'Set registration date to a greater period.')
                        % date_range.name
                    )
        # do not super() to avoid raise of original function
        # return super(AccountInvoice, self)._check_invoice_reference()

    @api.multi
    def action_cancel(self):
        for invoice in self:
            date_range_type = self.env['date.range.type'].search(
                [('fiscal_year', '=', True)])
            date_range = self.env['date.range'].search([
                ('date_start', '<=', invoice.date_invoice),
                ('date_end', '>=', invoice.date_invoice),
                ('type_id', '!=', date_range_type.id),
            ])
            vat_statement = self.env[
                'account.vat.period.end.statement'].search(
                [('date_range_ids', 'in', date_range.id)])
            if vat_statement:
                if vat_statement[0].state != 'draft':
                    raise UserError(
                        _('Period %s have already a closed vat statement. '
                          'Reset to draft vat statement to cancel this '
                          'invoice.')
                        % date_range.name
                    )
        return super(AccountInvoice, self).action_cancel()
