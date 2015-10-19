# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 SimplERP srl (<http://www.simplerp.it>).
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

from openerp import models
import re
from datetime import datetime
from openerp import tools


class task(models.Model):
    _inherit = "project.task"

    def time_string_to_decimals(self, time_string, part_day):
        fields = time_string.split(":")
        adjust = 0.0
        if part_day[0] == 'P' and fields[0] != '12':
            adjust = 11.0
        hours = fields[0] if len(fields) > 0 else 0.0
        minutes = fields[1] if len(fields) > 1 else 0.0
        seconds = fields[2] if len(fields) > 2 else 0.0
        return float(hours) + adjust + (float(minutes) / 60.0) + (float(seconds) / pow(60.0, 2))

    def create(self, cr, uid, vals, context=None):
        task_id = super(task, self).create(cr, uid, vals, context=context)
        name = vals.get('name', False)
        if re.search('annullato', name):
            return task_id
        m = re.search('[0-9]{,1}[0-9] [a-z][a-z][a-z] 20[0-9][0-9]', name)
        if m:
            # if more than 1 occurrence, take the 2°?
            datet_work = datetime.strptime(m.group(0), '%d %b %Y')
            hours = re.search('[0-9]{,1}[0-9](:[0-9][0-9]){,1}[AP]M - [0-9]{,1}[0-9](:[0-9][0-9]){,1}[AP]M', name).group(0)
            hours_start = self.time_string_to_decimals(hours[:(hours.find(' - ')) - 2], hours[(hours.find(' - ')) - 2:(hours.find(' - '))])
            hours_end = self.time_string_to_decimals(hours[(hours.find(' - ')) + 3: - 2], hours[(hours.find(' - ')):][-2:])
            # if more than 1 occurrence, take the 2°?
            hours_work = 0.0
            if hours:
                hours_work = hours_end - hours_start
            project_id = vals.get('project_id', False)
            if name and project_id:
                task_work = self.pool['project.task.work']
                work_vals = {
                    'name': name,
                    'task_id': task_id,
                    'date': datet_work.strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT),
                    'hours': hours_work,
                    'user_id': uid,
                }
                task_work.create(cr, uid, work_vals, context=context)
        return task_id


class project(models.Model):
    _inherit = "project.project"

    _defaults = {
        'use_tasks': True,
        'use_timesheets': True,
    }


class account_analytic_account(models.Model):
    _inherit = "account.analytic.account"

    def _get_100_percent(self, cr, uid, context):
        ids = self.pool.get('hr_timesheet_invoice.factor').search(
            cr, uid, [('name', 'ilike', '100')], context=context)
        return ids[0]

    _defaults = {
        'use_tasks': True,
        'use_timesheets': True,
        'to_invoice': _get_100_percent,
    }
