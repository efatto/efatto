# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, _
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class PrintWeeklyHoursTemplate(models.AbstractModel):
    _name = 'report.employee_check_inout.print_weekly_hours_template'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name(
            'employee_check_inout.print_weekly_hours_template')
        docargs = {
            'doc_ids': self.env["wizard.weekly.hours"].browse(data["ids"]),
            'doc_model': report.model,
            'docs': self,
            'get_attendance_list': self._get_attendance_list,
            'get_employee_data': self._get_employee_data,
            'get_date': self._get_date,
            'data': data
        }
        return report_obj.render(
            'employee_check_inout.print_weekly_hours_template', docargs)

    @staticmethod
    def _get_date(date):
        if date:
            date = (datetime.strptime(date, "%Y-%m-%d")).strftime('%d/%m/%Y')
        return date

    @api.multi
    def _get_employee_data(self, data):
        employee_data = []
        if data.get('form') and data.get('form').get('employee_id'):
            employee_id = self.env['hr.employee'].search(
                [('id', '=', data.get('form').get('employee_id'))])
            employee_data.append(
                {'name': employee_id.name, 'image': employee_id.image_medium})
        return employee_data

    @api.multi
    def _get_attendance_list(self, data):
        attendance_list = []
        if data.get('form') and data.get('form').get('start_date') and \
                data.get('form').get('end_date') and \
                data.get('form').get('employee_id'):
            attendance_obj = self.env['hr.attendance']
            attendance_ids = attendance_obj.search([
                ('employee_id', '=', data.get('form').get('employee_id')),
                ('name', '>=', data.get('form').get('start_date')),
                ('name', '<=', data.get('form').get('end_date'))], order='id')
            check_in = ''
            for attendance in attendance_ids:
                if attendance.action == 'sign_in':
                    check_in = datetime.strptime(
                        attendance.name, DEFAULT_SERVER_DATETIME_FORMAT)
                elif attendance.action == 'sign_out':
                    check_out = datetime.strptime(
                        attendance.name, DEFAULT_SERVER_DATETIME_FORMAT)
                    duration = check_out - check_in
                    duration_minuts = int(duration.total_seconds()/60)
                    if duration_minuts >= 0:
                        duration_hours = ('%.2f' % (duration_minuts/60.0))
                        attendance_list.append({
                            'total_hours_worked': duration_hours,
                            'total_minuts_worked': duration_minuts,
                            'check_in': check_in.strftime(
                                DEFAULT_SERVER_DATETIME_FORMAT) or '',
                            'check_out': check_out.strftime(
                                DEFAULT_SERVER_DATETIME_FORMAT) or '',
                        })
        return attendance_list
