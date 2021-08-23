# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class GeneralLedgerReportWizard(models.TransientModel):
    _inherit = "general.ledger.report.wizard"

    group_method = fields.Selection([
        ('group_payments', 'Group payments'),
        ('group_invoices', 'Group Invoices'),
        ('no_group', 'No Group')
    ], string="Group method", default='no_group')

    def _prepare_report_general_ledger(self):
        res = super()._prepare_report_general_ledger()
        res.update({
            'group_method': self.group_method,
        })
        return res
