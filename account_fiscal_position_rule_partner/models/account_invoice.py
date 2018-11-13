# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, _
from openerp.exceptions import Warning as UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_number(self):
        res = super(AccountInvoice, self).action_number()
        for inv in self:
            if inv.account_fiscal_position_rule_id and inv.type in [
                'out_invoice',
            ]:
                if inv.account_fiscal_position_rule_id.amount_max < \
                        inv.account_fiscal_position_rule_id.amount_total + \
                        inv.amount_untaxed:
                    raise UserError(
                        _('Fiscal position rule residual amount %.2f is not '
                          'enough to validate this invoice with amount %.2f. '
                          'Remove fiscal position rule to continue.')
                        % (inv.account_fiscal_position_rule_id.amount_max -
                           inv.account_fiscal_position_rule_id.amount_total,
                           inv.amount_untaxed)
                    )
        return res

    @api.multi
    def button_reset_taxes(self):
        res = super(AccountInvoice, self).button_reset_taxes()
        for inv in self:
            if inv.account_fiscal_position_rule_id and inv.type in [
                'out_invoice',
            ]:
                if inv.account_fiscal_position_rule_id.amount_max < \
                        inv.account_fiscal_position_rule_id.amount_total + \
                        inv.amount_untaxed:
                    raise UserError(
                        _('Fiscal position rule residual amount %.2f is not '
                          'enough to validate this invoice with amount %.2f. '
                          'Remove fiscal position rule to continue.')
                        % (inv.account_fiscal_position_rule_id.amount_max -
                           inv.account_fiscal_position_rule_id.amount_total,
                           inv.amount_untaxed)
                    )
        return res
