# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_reconcile(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move.line',
            'views': [[False, 'tree'], [False, 'form']],
            'domain': [
                ['account_id', '=', self.account_id.id],
                ['reconcile_id', '=', False],
                ['period_id.special', '=', False],
                ['partner_id', '=', self.partner_id.id],
            ],
        }
