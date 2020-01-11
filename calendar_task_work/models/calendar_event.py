
from odoo import models, fields, api, _, exceptions


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    @api.multi
    def _get_task_done(self):
        for event in self.sudo():
            if event.project_task_id.stage_id.state == 'done':
                event.task_done = True

    @api.multi
    def _get_timesheet_done(self):
        for event in self.sudo():
            if event.project_task_id.timesheet_ids:
                #TODO more specific check on attendes by percent?
                # for partner_id in event.partner_ids:
                #     user = self.env['res.users'].search(
                #         [('partner_id', '=', partner_id.id)], limit=1)
                #     # todo test if all lines are correct with times recorded
                #     # if not, user has changed time in event and timesheet
                #     # is no more correct
                #     if user:
                #         employee = self.env['hr.employee'].search(
                #             [('user_id', '=', user[0].id)])
                #         if employee:
                #             timesheet = event.timesheet_ids.filtered(
                #                 lambda x: x.user_id == user and
                #                 x.task_id == event.project_task_id
                #             )
                #             if timesheet:
                event.timesheet_done = True

    project_id = fields.Many2one(
        comodel_name='project.project',
        string='Project'
    )
    project_task_id = fields.Many2one(
        comodel_name='project.task',
        string='Project task'
    )
    timesheet_ids = fields.One2many(
        related='project_task_id.timesheet_ids',
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
                'calendar',
                'view_calendar_event_form')
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
