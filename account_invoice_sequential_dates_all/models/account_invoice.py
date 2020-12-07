# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, _, fields
from openerp.exceptions import Warning as UserError
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_number(self):
        res = super(AccountInvoice, self).action_number()
        for invoice in self:
            # ----- NOT Ignore supplier invoice and supplier refund
            # check until last date of registration year only
            registration_fy_id = self.env['account.fiscalyear'].find(
                dt=invoice.registration_date)
            if not registration_fy_id:
                raise UserError(_('Fiscal Year not found for registration'
                                  ' date requested'))
            fy = self.env['account.fiscalyear'].browse(registration_fy_id)
            existing_invoice = self.search([
                ('type', '=', invoice.type),
                ('registration_date', '>', invoice.registration_date),
                ('number', '<', invoice.number),
                ('journal_id', '=', invoice.journal_id.id),
                ('registration_date', '<=', fy.date_stop),
            ],
                order='registration_date desc', limit=1,
            )
            if existing_invoice:
                raise UserError(
                    _('Cannot create invoice! Post the invoice'
                      ' with an equal or greater date than %s')
                    % datetime.strptime(
                        existing_invoice.registration_date,
                        DEFAULT_SERVER_DATE_FORMAT).strftime('%d/%m/%Y')
                )
        return res