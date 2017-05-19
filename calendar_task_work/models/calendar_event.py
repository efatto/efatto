# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _, exceptions


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    @api.multi
    def _get_task_done(self):
        for event in self:
            if event.project_task_id.stage_id.state == 'done':
                event.task_done = True

    @api.multi
    def _get_timesheet_done(self):
        for event in self:
            if event.timesheet_ids:
                for partner_id in event.partner_ids:
                    user = self.env['res.users'].search(
                        [('partner_id', '=', partner_id.id)], limit=1)
                    if user:
                        employee = self.env['hr.employee'].search(
                            [('user_id', '=', user[0].id)])
                        if employee:
                            timesheet = event.timesheet_ids.filtered(
                                lambda x: x.user_id == user)
                            if timesheet:
                                event.timesheet_done = True

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
        string='Task work records'
    )
    timesheet_ids = fields.One2many(
        comodel_name='hr.analytic.timesheet',
        inverse_name='event_id',
        string='Timesheet records'
    )
    task_done = fields.Boolean(
        compute='_get_task_done',
    )
    timesheet_done = fields.Boolean(
        compute='_get_timesheet_done',
    )

    @api.onchange('project_id')
    def onchange_project_id(self):
        self.project_task_id = False

    @api.multi
    @api.depends('project_id', 'project_task_id')
    def record_task_work(self):
        # res_ids = []
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
                user = self.env['res.users'].search(
                    [('partner_id', '=', partner_id.id)], limit=1)
                if user:
                    employee = self.env['hr.employee'].search(
                        [('user_id', '=', user[0].id)])
                    if employee:
                        timesheet = event.timesheet_ids.filtered(
                            lambda x: x.user_id == user)
                        if timesheet:
                            # If timesheet for this user exists, update it
                            timesheet.unit_amount = round(duration, 2)
                        # Else create ANALYTIC entry wich create task work
                        else:
                            self.env[
                                'hr.analytic.timesheet'].create({
                                    'name': event.name,
                                    'date': event.start_datetime,
                                    'task_id': event.project_task_id.id,
                                    'unit_amount': round(duration, 2),
                                    'account_id': event.project_id.\
                                    analytic_account_id.id,
                                    'journal_id': employee.journal_id.id,
                                    'user_id': user.id,
                                    'company_id': user.company_id.id,
                                    'event_id': event.id,
                            })
            return True

    @api.multi
    def set_task_done(self):
        state_done = self.env['project.task.type'].search([
            ('state', '=', 'done')
        ], limit=1)
        for event in self:
            if state_done and event.project_task_id:
                event.project_task_id.stage_id = state_done
            else:
                raise exceptions.ValidationError(_(
                    '%s' % (not state_done and 'Missing state of type done'
                            or 'Missing task')
                ))
        return True


class TaskWork(models.Model): # not more used
    _inherit = 'project.task.work'

    event_id = fields.Many2one(
        comodel_name='calendar.event',
        string='Calendar event',
    )


class Timesheet(models.Model):
    _inherit = 'hr.analytic.timesheet'

    event_id = fields.Many2one(
        comodel_name='calendar.event',
        string='Calendar event',
    )
