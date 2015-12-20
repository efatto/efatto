# -*- coding: utf-8 -*-
#
#
#    Copyright (C) 2015 SimplERP srl (<http://www.simplerp.it>).
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
