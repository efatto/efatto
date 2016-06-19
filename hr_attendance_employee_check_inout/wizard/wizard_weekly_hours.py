# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import fields, models, api, _
from datetime import date, timedelta


class WizardWeeklyHours(models.TransientModel):
    _name = "wizard.weekly.hours"

    @api.model
    def get_week_first_day(self):
        return date.today() - timedelta(days=date.today().weekday())

    @api.model
    def get_current_date(self):
        return date.today()

    start_date = fields.Date(
        string="Start Date", default=get_week_first_day, required=True)
    end_date = fields.Date(
        string="End Date", default=get_current_date, required=True)

    @api.multi
    def print_weekly_hours_report(self):
        data = self.read()[0]
        if self._context.get('active_id'):
            data.update({'employee_id': self._context.get('active_id')})
        datas = {
            'ids': self._ids,
            'model': 'wizard.weekly.hours',
            'form': data
        }
        return self.env['report'].get_action(
            self,
            'hr_attendance_employee_check_inout.print_weekly_hours_template',
            data=datas,)
