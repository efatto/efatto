# -*- encoding: utf-8 -*-
##############################################################################
#    Copyright (c) 2012 - Present Acespritech Solutions Pvt. Ltd. All Rights Reserved
#    Author: <info@acespritech.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of the GNU General Public License is available at:
#    <http://www.gnu.org/licenses/gpl.html>.
#
##############################################################################

from openerp import fields, models, api, _
from datetime import date, datetime, timedelta


class wizard_weekly_hours(models.TransientModel):
    _name = "wizard.weekly.hours"

    @api.model
    def get_week_first_day(self):
        return date.today() - timedelta(days=date.today().weekday())

    @api.model
    def get_current_date(self):
         return date.today()

    start_date = fields.Date(string="Start Date", default=get_week_first_day, required=True)
    end_date = fields.Date(string="End Date", default=get_current_date, required=True)

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
        return  self.env['report'].get_action(self, 'employee_check_inout.print_weekly_hours_template', data=datas,)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: