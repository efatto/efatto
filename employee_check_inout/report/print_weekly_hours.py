# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2013-Present Acespritech Solutions Pvt. Ltd. (<http://acespritech.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, api, _
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class print_weekly_hours_template(models.AbstractModel):
    _name = 'report.employee_check_inout.print_weekly_hours_template'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('employee_check_inout.print_weekly_hours_template')
        docargs = {
            'doc_ids': self.env["wizard.weekly.hours"].browse(data["ids"]),
            'doc_model': report.model,
            'docs': self,
            'get_attendance_list': self._get_attendance_list,
            'get_employee_data': self._get_employee_data,
            'get_date': self._get_date,
            'data': data
        }
        return report_obj.render('employee_check_inout.print_weekly_hours_template', docargs)

    def _get_date(self, date):
        if date:
            date = (datetime.strptime(date, "%Y-%m-%d")).strftime('%d/%m/%Y')
        return date

    def _get_employee_data(self, data):
        employee_data = []
        if data.get('form') and data.get('form').get('employee_id'):
            employee_id = self.env['hr.employee'].search([('id', '=', data.get('form').get('employee_id'))])
            employee_data.append({'name': employee_id.name, 'image': employee_id.image_medium})
        return employee_data

    def _get_attendance_list(self, data):
        if data.get('form') and data.get('form').get('start_date') and data.get('form').get('end_date')\
                and data.get('form').get('employee_id'):
            attendance_obj = self.env['hr.attendance']
            attendance_ids = attendance_obj.search([('employee_id', '=', data.get('form').get('employee_id')),
                                                               ('name', '>=', data.get('form').get('start_date')),
                                                               ('name', '<=', data.get('form').get('end_date'))],
                                                               order='id')
            attendance_list = []
            check_in = ''
            for attendance in attendance_ids:
                if attendance.action == 'sign_in':
                    check_in = datetime.strptime(attendance.name, DEFAULT_SERVER_DATETIME_FORMAT)
                elif attendance.action == 'sign_out':
                    check_out = datetime.strptime(attendance.name, DEFAULT_SERVER_DATETIME_FORMAT)
                    duration = check_out - check_in
                    duration_minuts = int(duration.total_seconds()/60)
                    if duration_minuts >= 0:
                        duration_hours = ('%.2f' % (duration_minuts/60.0))
                        attendance_list.append({
                            'total_hours_worked': duration_hours,
                            'check_in': check_in.strftime("%d/%m/%Y") or '',
                            'check_out': check_out.strftime("%d/%m/%Y") or '',
                        })
        return attendance_list
