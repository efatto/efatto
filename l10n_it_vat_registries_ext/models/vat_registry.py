# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp.addons.l10n_it_vat_registries.vat_registry import Parser
from openerp.osv import osv
from datetime import datetime


class VatRegistryParser(Parser):

    def _get_fy(self, period_ids):
        period_obj = self.pool['account.period']
        fy_obj = self.pool['account.fiscalyear']
        end_date = False
        for period in period_obj.browse(
            self.cr, self.uid,
            period_ids,
        ):
            period_end = datetime.strptime(period.date_stop, '%Y-%m-%d')
            if not end_date or end_date < period_end:
                end_date = period_end
        fy = fy_obj.find(self.cr, self.uid, period_end)
        fy_code = fy_obj.browse(self.cr, self.uid, [fy]).code
        return fy_code

    def __init__(self, cr, uid, name, context):
        super(VatRegistryParser, self).__init__(cr, uid, name, context=context)

    def set_context(self, objects, data, ids, report_type=None):
        self.localcontext.update({
            'l10n_it_fiscalyear_code': self._get_fy(
                data['form'].get('period_ids')),
        })
        return super(VatRegistryParser, self).set_context(
            objects, data, ids, report_type=report_type)

class ReportRegistroIvaVendite(osv.AbstractModel):
    _inherit = 'report.l10n_it_vat_registries.report_registro_iva'
    _wrapped_report_class = VatRegistryParser
