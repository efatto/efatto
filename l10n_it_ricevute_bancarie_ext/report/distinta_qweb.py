# -*- coding: utf-8 -*-
# © 2016 Andrea Cometa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime


class DistintaReportQweb(models.AbstractModel):
    _inherit = 'report.l10n_it_ricevute_bancarie.distinta_qweb'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name(
            'l10n_it_ricevute_bancarie.distinta_qweb')
        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'company': False,
            'docs': self.env[report.model].browse(self._ids),
            'get_riba_group': self._get_riba_group(
                self.env[report.model].browse(self._ids)
            ),
        }
        return report_obj.render(
            'l10n_it_ricevute_bancarie.distinta_qweb',
            docargs)

    def _get_riba_group(self, objects):
        res = {}
        for distinta in objects:
            for line in distinta.line_ids:
                line_due_date = datetime.strptime(
                    line.due_date, DEFAULT_SERVER_DATE_FORMAT
                ).strftime('%d/%m/%Y')
                if not line_due_date in res:
                    res.update({line_due_date: [line]})
                else:
                    res[line_due_date] = res[line_due_date] + [line]
        return res
