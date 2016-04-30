# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import api, models


class AccountReport(models.AbstractModel):
    _name = 'report.account_smart_reporting.report_account_smart'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name(
            'account_smart_reporting.report_account_smart')
        active_ids = self._context['default_active_ids']
        docargs = {
            'doc_ids': active_ids,
            'doc_model': report.model,
            'docs': self.env[self._context['active_model']].browse(active_ids),
        }
        return report_obj.render(
            'account_smart_reporting.report_account_smart', docargs)
