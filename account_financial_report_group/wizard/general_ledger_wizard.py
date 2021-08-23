# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class GeneralLedgerReportWizard(models.TransientModel):
    _inherit = "general.ledger.report.wizard"

    group_method = fields.Selection([
        ('group_payments', 'Merge payments'),
        ('group_invoices', 'Group Invoices'),
        ('no_group', 'No Group')
    ], string="Group method", default='no_group',
        help='Group payments will merge rows which differs only for credit, debit, '
             'balance and date maturity values, so when an invoice has multiple rows '
             'of payment with differents maturity dates, them will be grouped.\n'
             'Group invoices will group rows by invoices, showing first payment for '
             'invoices not present in current report, then invoices with related '
             'payment, lastly invoices not yet reconciled.')

    def _prepare_report_general_ledger(self):
        res = super()._prepare_report_general_ledger()
        res.update({
            'group_method': self.group_method,
        })
        return res
