
from odoo import models, fields, api, _, exceptions


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    @api.multi
    def _get_task_done(self):
        for event in self.sudo():
            if event.project_task_id.stage_id.state == 'done':
                event.task_done = True

    @api.multi
    @api.depends('project_task_id.timesheet_ids', 'user_id', 'start_datetime',
                 'stop_datetime')
    def _get_timesheet_done(self):
        for event in self.sudo():
            done = False
            if event.project_task_id.timesheet_ids:
                employee = self.env['hr.employee'].search(
                    [('user_id', '=', event.user_id.id)])
                if employee:
                    timesheet = event.project_task_id.timesheet_ids.filtered(
                        lambda x: x.employee_id == employee
                        and x.date_time == event.start_datetime
                    )
                    if timesheet:
                        done = True
            event.done = done

    project_id = fields.Many2one(
        comodel_name='project.project',
        string='Project'
    )
    project_task_id = fields.Many2one(
        comodel_name='project.task',
        string='Project task'
    )
    sale_line_id = fields.Many2one(
        related='project_task_id.sale_line_id',
        string='Sale line'
    )
    timesheet_ids = fields.One2many(
        related='project_task_id.timesheet_ids',
        string='Timesheet records'
    )
    task_done = fields.Boolean(
        compute='_get_task_done',
    )
    done = fields.Boolean(
        compute='_get_timesheet_done', store=False
    )
    work_done = fields.Boolean(
        related='done', store=True
    )

    @api.onchange('project_id')
    def onchange_project_id(self):
        self.project_task_id = False

    @api.multi
    @api.depends('project_id', 'project_task_id')
    def record_task_work(self):
        for event in self:
            # record task work for this task for only user owner of this event
            stop_datetime = event.stop_datetime
            start_datetime = event.start_datetime
            if not (stop_datetime or start_datetime):
                raise exceptions.ValidationError(_(
                    'Missing date start or date stop'))
            diff = fields.Datetime.from_string(stop_datetime) - \
                fields.Datetime.from_string(start_datetime)
            if diff:
                duration = float(diff.days) * 24 + (float(diff.seconds) / 3600)

            employee = self.env['hr.employee'].search(
                [('user_id', '=', event.user_id.id)])
            if employee:
                timesheet = event.project_task_id.timesheet_ids.filtered(
                    lambda x: x.employee_id == employee
                    and x.date_time == event.start_datetime)
                # todo extend filter to event + timedelta(duration)?
                # If analytic line for this user exists, update it
                if timesheet:
                    timesheet.write({
                        'name': event.name,
                        'unit_amount': round(duration, 2),
                        'amount': round(duration, 2) * employee.timesheet_cost,
                    })
                # Else create
                else:
                    self.env['account.analytic.line'].create({
                        'name': event.name,
                        'employee_id': employee.id,
                        'date_time': event.start_datetime,
                        'project_id': event.project_id.id,
                        'task_id': event.project_task_id.id,
                        'unit_amount': round(duration, 2),
                        'amount': employee.timesheet_cost * round(duration, 2),
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


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    event_id = fields.Many2one(
        comodel_name='calendar.event',
        string='Calendar event',
    )

    @api.multi
    def action_view_event(self):
        view_rec = self.env['ir.model.data'].get_object_reference(
            'calendar', 'view_calendar_event_form')
        view_id = False
        if view_rec:
            view_id = view_rec and view_rec[1] or False
        res_id = self._context.get('default_event_id', False)
        return {
            'view_type': 'form',
            'name': "Event",
            'view_id': [view_id],
            'res_id': res_id,
            'view_mode': 'form',
            'res_model': 'calendar.event',
            'type': 'ir.actions.act_window',
            'views': [[False, 'tree'], [False, 'form']],
            'domain': [['id', '=', res_id]],
        }
