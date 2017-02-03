# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _


class HrAnalyticTimesheet(models.Model):
    _inherit = 'hr.analytic.timesheet'

    task_id = fields.Many2one(
        comodel_name='project.task',
        string='Task',
    )

    #TODO when create analytic timesheet directly, create project.task.work (be careful
    #TODO to not recreate analytic timesheet and so on circular!!)

    @api.model
    def create(self, vals):
        res = super(HrAnalyticTimesheet, self).create(vals)
        if vals.get('task_id', False):
            date = vals['date']
            if date == fields.Date.today():
                date = fields.Datetime.now()
            values = {
                'name': vals['name'],
                'date': date,
                'task_id': vals['task_id'],
                'hours': vals['unit_amount'],
                'user_id': vals['user_id'],
                'company_id': self.env['res.users'].browse(
                    vals['user_id']).company_id.id,
                'hr_analytic_timesheet_id': res.id,
            }
            self.env['project.task.work'].with_context(
                {'no_analytic_entry': True}).create(values)
        return res

    #todo when modify, adjust task work
    @api.multi
    def write(self, vals):
        for line in self:
            if line.task_id or vals.get('task_id', False):
                date = vals.get('date', False) or line.date
                if date == fields.Date.today():
                    date = fields.Datetime.now()
                user = vals.get('user_id', False) or line.user_id.id
                task_work = self.env['project.task.work'].search([
                    ('hr_analytic_timesheet_id', '=', line.id)
                ])
                if task_work:
                    task_work.with_context({'no_analytic_entry': True}).write({
                        'name': vals.get('name', False) or line.name,
                        'date': date,
                        'task_id': vals.get('task_id', False) or line.task_id.id,
                        'hours': vals.get('unit_amount', False) or
                        line.unit_amount,
                        'user_id': user,
                        'company_id': self.env['res.users'].browse(
                            user).company_id.id,
                    })
        return super(HrAnalyticTimesheet, self).write(vals)

class ProjectWork(models.Model):
    _inherit = "project.task.work"

    @api.model
    def _create_analytic_entries(self, vals):
        timeline_id = super(ProjectWork, self)._create_analytic_entries(
            vals=vals)
        if vals.get('task_id', False):
            self.env['hr.analytic.timesheet'].browse(timeline_id).task_id = \
            vals['task_id']
        return timeline_id

    @api.multi
    def write(self, vals):
        # Bypass original write method to avoid recursion generated from
        # project_timesheet
        if self.env.context.get('no_analytic_entry', False):
            if 'hours' in vals and (not vals['hours']):
                vals['hours'] = 0.00
            if 'hours' in vals:
                for work in self:
                    self._cr.execute(
                        'update project_task set remaining_hours='
                        'remaining_hours - %s + (%s) where id=%s',
                        (vals.get('hours', 0.0), work.hours, work.task_id.id))
                    self.invalidate_cache()
            return super(models.Model, self).write(vals)
        return super(ProjectWork, self).write(vals)
