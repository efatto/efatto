# -*- coding: utf-8 -*-
#
#
#    Copyright (C) 2011-2013 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>).
#    Copyright (C) 2014-2015 Agile Business Group sagl
#    (<http://www.agilebg.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

from openerp.report import report_sxw
from openerp.osv import osv
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class Parser(report_sxw.rml_parse):

    def _get_move(self, move_ids):
        move_list = self.pool.get(
            'account.move').browse(self.cr, self.uid, move_ids)
        return move_list

    def _get_start_date(self):
        period_obj = self.pool.get('account.period')
        start_date = False
        for period in period_obj.browse(
            self.cr, self.uid,
            self.localcontext['data']['form']['period_ids']
        ):
            period_start = datetime.strptime(period.date_start, '%Y-%m-%d')
            if not start_date or start_date > period_start:
                start_date = period_start
        return start_date.strftime('%Y-%m-%d')

    def _get_end_date(self):
        period_obj = self.pool.get('account.period')
        end_date = False
        for period in period_obj.browse(
            self.cr, self.uid,
            self.localcontext['data']['form']['period_ids']
        ):
            period_end = datetime.strptime(period.date_stop, '%Y-%m-%d')
            if not end_date or end_date < period_end:
                end_date = period_end
        return end_date.strftime('%Y-%m-%d')

    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_move': self._get_move,
            'start_date': self._get_start_date,
            'end_date': self._get_end_date,
        })

    def set_context(self, objects, data, ids):
        self.localcontext.update({
            'l10n_it_count_fiscal_page_base': data['form'].get(
                'fiscal_page_base'),
        })
        return super(Parser, self).set_context(
            objects, data, ids)


class ReportFiscalJournal(osv.AbstractModel):
    _name = 'report.l10n_it_fiscal_journal.report_fiscal_journal'
    _inherit = 'report.abstract_report'
    _template = 'l10n_it_fiscal_journal.report_fiscal_journal'
    _wrapped_report_class = Parser
