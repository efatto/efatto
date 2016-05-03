# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
import logging
from openerp import api, models

_logger = logging.getLogger(__name__)


class AccountReport(models.AbstractModel):
    _name = 'report.account_smart_reporting.report_account_smart'
    _inherit = 'report.abstract_report'
    _template = 'account_smart_reporting.report_account_smart'

    @api.multi
    def render_html(self, data=None):
        active_ids = self._context['default_active_ids']
        doc_type = 'in'
        for invoice in self.env['account.invoice'].browse(active_ids):
            if invoice.type in ['out_invoice', 'out_refund']:
                doc_type = 'out'

        docargs = {
            'doc_ids': active_ids,
            'doc_model': 'account.invoice',
            'doc_type': doc_type,
            'docs': self.env[self._context['active_model']].browse(active_ids),
        }
        return self.env['report'].render(
            'account_smart_reporting.report_account_smart', docargs)
