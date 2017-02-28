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
    timesheet_ids = fields.One2many(
        comodel_name='hr.analytic.timesheet',
        inverse_name='task_id',
        string='Timesheet records'
    )

    @api.onchange('project_id')
    def onchange_project_id(self):
        self.project_task_id = False

    @api.multi
    def record_timesheet(self):
        for event in self:
            #  TODO record timesheet for this task for these users
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
                    [('partner_id', '=', partner_id.id)])
                if user:
                    employee = self.env['hr.employee'].search(
                        [('user_id', '=', user[0].id)])
                    if employee:
                        if event.timesheet_ids:
                            #  if timesheet for this user exists, update it
                            timesheet = event.timesheet_ids.filtered(
                                lambda x: x.user_id == user)
                            if timesheet:
                                timesheet.unit_amount = round(duration, 2)
                        #  else create
                        else:
                            timesheet_id = self.env[
                                'hr.analytic.timesheet'].with_context(
                                {'no_task_creation': True,
                                 'user_id': user.id}).create({
                                    'date': event.start_datetime,
                                    'name': event.name,
                                    'user_id': user.id,
                                    'account_id': event.project_id.
                                    analytic_account_id.id,
                                    'task_id': event.project_task_id.id,
                                    'unit_amount': round(duration, 2),
                                    'to_invoice': False,
                                    'journal_id': employee.journal_id.id,
                            })
                            event.write({
                                'timesheet_ids': [(4, timesheet_id.id)]})
