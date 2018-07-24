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
                                lambda x: x.user_id == user and
                                x.task_id == event.project_task_id
                            )
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
            #  record task work for this task for these users
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
                        result = self.env['project.task.work'].\
                            get_user_related_details(user.id)
                        timesheet = event.timesheet_ids.filtered(
                            lambda x: x.user_id == user)
                        if timesheet:
                            # If timesheet for this user exists, update it
                            timesheet.write({
                                'name': event.name,
                                'date': event.start_datetime,
                                'task_id': event.project_task_id.id,
                                'unit_amount': round(duration, 2),
                                'account_id': event.project_id.\
                                analytic_account_id.id,
                                'product_id': result['product_id'],
                                'general_account_id': result[
                                    'general_account_id'],
                                'product_uom_id': result['product_uom_id'],
                            })
                        # Else create ANALYTIC entry wich create task work
                        else:
                            timesheet = self.env[
                                'hr.analytic.timesheet'].create({
                                    'name': event.name,
                                    'date': event.start_datetime,
                                    'task_id': event.project_task_id.id,
                                    'unit_amount': round(duration, 2),
                                    'account_id': event.project_id.\
                                    analytic_account_id.id,
                                    'journal_id': result['journal_id'],
                                    'user_id': user.id,
                                    'company_id': user.company_id.id,
                                    'event_id': event.id,
                                    'product_id': result['product_id'],
                                    'general_account_id': result[
                                        'general_account_id'],
                                    'product_uom_id': result['product_uom_id'],
                            })
                        amount_unit = timesheet.on_change_unit_amount(
                            result['product_id'], round(duration, 2),
                            False, False, result['journal_id'])[0]
                        if amount_unit and 'amount' in amount_unit.get(
                                'value', {}):
                            amount = amount_unit['value']['amount']
                        to_invoice = event.project_id.analytic_account_id.\
                            to_invoice.id
                        timesheet.write({
                            'amount': amount,
                            'to_invoice': to_invoice,})
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

    @api.multi
    def write(self, vals):
        for ts in self:
            if ts.event_id and not self._context.get(
                    'update_event_from_ts', False) and (
                        vals.get('account_id', False) or
                        vals.get('task_id', False)):
                raise exceptions.ValidationError(_(
                    'This timesheet is generated from calendar view! '
                    'Project and task can be changed from linked event.'
                ))
        return super(Timesheet, self).write(vals)

    @api.multi
    def action_view_event(self):
        view_rec = self.env['ir.model.data'].get_object_reference(
                'calendar',
                'view_calendar_event_form')
        view_id = False
        if view_rec:
            view_id = view_rec and view_rec[1] or False
        res_id = self._context.get('default_event_id', False)
        ctx = self._context.copy()
        ctx.update(update_event_from_ts=True)
        return {
            'view_type': 'form',
            'name': "Event",
            'view_id': [view_id],
            'res_id': res_id,
            'view_mode': 'form',
            'res_model': 'calendar.event',
            'type': 'ir.actions.act_window',
            'context': ctx,
            'views': [[False, 'tree'], [False, 'form']],
            'domain': [['id', '=', res_id]],
        }
