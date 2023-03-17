# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import models, api


class ReportGiornale(models.AbstractModel):
    _inherit = 'report.l10n_it_central_journal.report_giornale'

    @staticmethod
    def _get_partner_history(date, partner_id):
        res = partner_id.name
        if partner_id.res_partner_history_ids:
            history = partner_id.res_partner_history_ids.filtered(
                lambda x: x.date_from <= date <= x.date_to)
            if history:
                res = history.name
        return res

    @api.model
    def _get_report_values(self, docids, data=None):
        res = super()._get_report_values(docids, data=data)
        res.update({
            'get_partner_history': self._get_partner_history,
        })
        return res
