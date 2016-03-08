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
from datetime import datetime, timedelta
from pytz import timezone
from openerp import tools


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
        attendance_list = []
        if data.get('form') and data.get('form').get('start_date') and data.get('form').get('end_date')\
            and data.get('form').get('employee_id') and self._context.get('tz'):
            attendance_ids = self.env['hr.attendance'].search([('employee_id', '=', data.get('form').get('employee_id')),
                                                               ('name', '>=', data.get('form').get('start_date')),
                                                               ('name', '<=', data.get('form').get('end_date'))],
                                                               order='id')
            for attendance in range(0, len(list(attendance_ids))):
                tz = timezone(self._context.get('tz'))
                c_time = datetime.now(tz)
                hour_tz = int(str(c_time)[-5:][:2])
                min_tz = int(str(c_time)[-5:][3:])
                check_in_date = datetime.strptime(attendance_ids[attendance].name,
                                                  tools.DEFAULT_SERVER_DATETIME_FORMAT) + \
                                                  timedelta(hours=hour_tz, minutes=min_tz)
                try:
                    if attendance_ids[attendance].action != 'sign_in' or not attendance_ids[attendance + 1]:
                        continue
                    check_out_date = datetime.strptime(attendance_ids[attendance + 1].name,
                                                       tools.DEFAULT_SERVER_DATETIME_FORMAT) + \
                                                       timedelta(hours=hour_tz, minutes=min_tz)
                    diff_hours = (check_in_date - check_out_date).total_seconds() / 3600
                    attendance_list.append({
                        'total_hours_worked' : str(int(abs(round(diff_hours, 0)))) + ' hours',
                        'check_in': check_in_date.strftime('%Y %m %d %I:%M %p') or '',
                        'check_out': check_out_date.strftime('%Y %m %d %I:%M %p') or ''
                    })
                except:
                    attendance_list.append({
                        'total_hours_worked' : '---',
                        'check_in': check_in_date.strftime('%Y %m %d %I:%M %p') or '',
                        'check_out': '---'
                    })
        return attendance_list

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
