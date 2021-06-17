# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models, api
import logging

_logger = logging.getLogger(__name__)


class ReportGiornale(models.AbstractModel):
    _inherit = 'report.l10n_it_central_journal.report_giornale'

    @api.model
    def _get_report_values(self, docids, data=None):
        res = super()._get_report_values(docids, data)
        res.update({
            'print_row': data['form']['print_row'],
            'date_move_line_from': data['form']['date_move_line_from'],
        })
        return res
