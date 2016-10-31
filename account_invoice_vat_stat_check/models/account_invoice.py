# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, _
from openerp.exceptions import Warning as UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    # @api.multi
    # def action_cancel(self):
    #     # TODO in many cases it is done to correct minor problems,
    #     # give the user the choice
    #     for obj_inv in self:
    #         period = obj_inv.period_id
    #         vat_statement = self.env[
    #             'account.vat.period.end.statement'].search(
    #                 [('period_ids', 'in', period.id)])
    #         if vat_statement:
    #             if vat_statement[0].state != 'draft':
    #                 raise UserError(
    #                     _('Period %s have already a closed vat statement. '
    #                       'Do not remove the invoice.')
    #                     % period.name
    #                 )
    #     return super(AccountInvoice, self).action_cancel()

    @api.multi
    def action_number(self):
        # TODO: this method is not invoked when the invoice is approved
        # without changes
        for obj_inv in self:
            period = obj_inv.period_id
            vat_statement = self.env[
                    'account.vat.period.end.statement'].search(
                    [('period_ids', 'in', period.id)])
            if vat_statement:
                if vat_statement[0].state != 'draft':
                    raise UserError(
                        _('Period %s have already a closed vat statement. '
                          'Set registration date to a greater period.')
                        % period.name
                    )
        return super(AccountInvoice, self).action_number()
