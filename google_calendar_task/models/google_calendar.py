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
from openerp import models


class google_calendar(models.AbstractModel):
    _inherit = 'google.calendar'

    def update_from_google(self, cr, uid, event, single_event_dict, type, context):
        res = super(google_calendar, self).update_from_google(cr, uid, event, single_event_dict, type, context)
        if not event:
            event_id = res
        else:
            event_id = event.id
        if res:
            calendar_event = self.pool['calendar.event']
            cal_event = calendar_event.browse(cr, uid, [event_id])
            task_obj = self.pool['project.task']
            task_id = task_obj.search(cr, uid, [('event_id', 'in', [event_id])])
            attendees = 'attendees' in single_event_dict and single_event_dict['attendees']
            mail_obj = self.pool['mail.alias']
            hours_work = cal_event.duration or False
            new = False
            project_id = False
            user_id = False
            #  if single_event_dict['creator']['email']:
            #  alias_creator = single_event_dict['creator']['email'].split('@')[0]
            #  N.B. creator is the calendar
            if single_event_dict['organizer']['email']:
                alias_organizer = single_event_dict['organizer']['email'].split('@')[0]
                user_id = self.pool['res.users'].search(cr, uid, [('alias_id', 'in', alias_organizer)])
                #  N.B. organizer must be the user login to sync - this is the user_id
            if attendees and hours_work:
                for attendant in attendees:
                    #  note: get only one occurrence of the creator, not investigated if only one possible
                    if 'email' in attendant and 'organizer' not in attendant:
                        project_alias_mail = attendant['email'].split('@')[0]
                        alias_id = mail_obj.search(cr, uid, [('alias_name', '=', project_alias_mail)])
                        project = self.pool['project.project'].search(cr, uid, [('alias_id', 'in', alias_id)])
                        if project:
                            project_id = project[0]
                        break
                if not task_id and cal_event.duration and project_id and user_id:
                    new = True
                    vals = {
                        'event_id': event_id,
                        'name': '',
                        'project_id': project_id,
                    }
                    task_id = [task_obj.create(cr, uid, vals, context=context)]
                task_work = self.pool['project.task.work']
                if project_id and new and user_id and task_id:
                    work_vals = {
                        'name': cal_event.name or '',
                        'task_id': task_id[0],
                        'date': cal_event.start_datetime,
                        'hours': hours_work,
                        'user_id': user_id[0],
                    }
                    task_work.create(cr, uid, work_vals, context=context)
                elif project_id and not new and user_id and task_id:
                    task = task_obj.browse(cr, uid, task_id, context)
                    if task.work_ids:
                        work_id = [x.id for x in task.work_ids][0]
                    work_vals = {
                        'name': cal_event.name or '',
                        'date': cal_event.start_datetime,
                        'hours': hours_work,
                        'user_id': user_id[0],
                    }
                    task_work.write(cr, uid, [work_id], work_vals, context=context)
        return res


class calendar_event(models.Model):
    _inherit = 'calendar.event'

    def unlink(self, cr, uid, ids, can_be_deleted=True, context=None):
        res = super(calendar_event, self).unlink(cr, uid, ids, can_be_deleted=can_be_deleted, context=context)
        if context is None:
            context = {}
        #  self._check_child_task(cr, uid, ids, context=context)
        #  note: task work are deleted automatically when task is deleted
        task = self.pool['project.task']
        task_id = task.search(cr, uid, [('event_id', 'in', [ids])])
        if task_id:
            task.unlink(cr, uid, task_id, context)
        return res
