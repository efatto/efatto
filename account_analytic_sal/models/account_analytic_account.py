# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.multi
    def _get_amount_sal_to_invoice(self):
        for account in self:
            account.amount_sal_to_invoice = sum([
                x.residual_toinvoice for x in account.account_analytic_sal_ids]
            )

    use_sal = fields.Boolean(
        string='Use SAL')
    account_analytic_sal_ids = fields.One2many(
        comodel_name='account.analytic.sal',
        inverse_name='account_analytic_id',
        string='Analytic SAL progression')
    amount_sal_to_invoice = fields.Float(
        compute=_get_amount_sal_to_invoice,
        help='Amount to invoice from SAL')
    invoice_line_ids = fields.One2many(
        string='Invoice lines',
        comodel_name='account.invoice.line',
        inverse_name='account_analytic_id')
