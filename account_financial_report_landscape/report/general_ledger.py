# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models,  _


class GeneralLedgerReportMoveLine(models.TransientModel):
    _inherit = 'report_general_ledger_move_line'

    date_maturity = fields.Date()


class GeneralLedgerReportCompute(models.TransientModel):
    _inherit = 'report_general_ledger'

    @api.multi
    def print_report(self, report_type):
        res = super().print_report(report_type)
        if report_type == 'qweb-pdf':
            report_name = 'account_financial_report_landscape.' \
                          'report_general_ledger_landscape_qweb'
            return self.env['ir.actions.report'].search(
                [('report_name', '=', report_name),
                 ('report_type', '=', report_type)],
                limit=1).report_action(self, config=False)
        return res
