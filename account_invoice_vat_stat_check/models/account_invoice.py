# -*- coding: utf-8 -*-

from odoo import models, api, _
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _check_invoice_reference(self):
        for invoice in self:
            date_range = self.env['date.range'].search([
                ('date_start', '<=', invoice.date_invoice),
                ('date_stop', '>=', invoice.date_invoice),
            ])
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
        return super(AccountInvoice, self)._check_invoice_reference()

    @api.multi
    def action_cancel(self):
        for invoice in self:
            date_range = self.env['date.range'].search([
                ('date_start', '<=', invoice.date_invoice),
                ('date_stop', '>=', invoice.date_invoice),
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
