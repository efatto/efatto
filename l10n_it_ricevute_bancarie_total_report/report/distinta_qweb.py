from datetime import datetime

from odoo import models


class DistintaReportQweb(models.AbstractModel):
    _inherit = "report.l10n_it_ricevute_bancarie.distinta_qweb"

    def _get_report_values(self, docids, data=None):
        res = super()._get_report_values(docids=docids, data=data)
        res.update(
            get_riba_group=self._get_riba_group(
                self.env["riba.distinta"].browse(docids)
            )
        )
        return res

    @staticmethod
    def _get_riba_group(objects):
        res = {}
        for distinta in objects:
            for line in distinta.line_ids:
                line_due_date = line.due_date.strftime("%d/%m/%Y")
                if line_due_date not in res:
                    res.update({line_due_date: [line]})
                else:
                    res[line_due_date] = res[line_due_date] + [line]
        dates = sorted([datetime.strptime(ts, "%d/%m/%Y") for ts in res])
        dates_sorted = [datetime.strftime(ts, "%d/%m/%Y") for ts in dates]
        return res, dates_sorted
