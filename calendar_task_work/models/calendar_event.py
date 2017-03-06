# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _, exceptions


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    project_id = fields.Many2one(
        comodel_name='project.project',
        string='Project'
    )
    project_task_id = fields.Many2one(
        comodel_name='project.task',
        string='Project task'
    )
    task_work_ids = fields.One2many(
        comodel_name='project.task.work',
        inverse_name='event_id',
        string='Timesheet records'
    )

    @api.onchange('project_id')
    def onchange_project_id(self):
        self.project_task_id = False

    @api.multi
    @api.depends('project_id', 'project_task_id')
    def record_task_work(self):
        res_ids = []
        for event in self:
            #  TODO record task work for this task for these users
            #  no problem if already recorded for same task or same users
            #  but one user can't have more than one timesheet for same time...
            stop_datetime = event.stop_datetime
            start_datetime = event.start_datetime
            if not (stop_datetime or start_datetime):
                raise exceptions.ValidationError(_(
                    'Missing date start or date stop'))
            diff = fields.Datetime.from_string(stop_datetime) - \
                fields.Datetime.from_string(start_datetime)
            if diff:
                duration = float(diff.days) * 24 + (float(diff.seconds) / 3600)
            for partner_id in event.partner_ids:
                work = False
                user = self.env['res.users'].search(
                    [('partner_id', '=', partner_id.id)])
                if user:
                    employee = self.env['hr.employee'].search(
                        [('user_id', '=', user[0].id)])
                    if employee:
                        if event.task_work_ids.filtered(
                                lambda x: x.user_id == user):
                            #  if works for this user exists, update it
                            work = event.task_work_ids.filtered(
                                lambda x: x.user_id == user)
                            work.hours = round(duration, 2)
                        #  else create
                        else:
                            work = self.env[
                                'project.task.work'].create({
                                    'date': event.start_datetime,
                                    'name': event.name,
                                    'user_id': user.id,
                                    'task_id': event.project_task_id.id,
                                    'hours': round(duration, 2),
                                    'event_id': event.id,
                                    'company_id': user.company_id.id,
                                })
                        if work:
                            res_ids.append(work.id)
            if res_ids:
                view = {
                    'name': _("Task work"),
                    'view_mode': 'tree',
                    'view_id': False,
                    'view_type': 'form',
                    'res_model': 'project.task.work',
                    'type': 'ir.actions.act_window',
                    'nodestroy': False,
                    'target': 'self',
                    'domain': [('id', 'in', res_ids)],
                    'context': self._context
                }
                return view

    @api.multi
    def set_task_completed(self):
        for event in self:
            if event.project_task_id:
                event.project_task_id.kanban_state = 'done'


class TaskWork(models.Model):
    _inherit = 'project.task.work'

    event_id = fields.Many2one(
        comodel_name='calendar.event',
        string='Calendar event',
    )
