# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _


class WizardProjectInclude(models.TransientModel):
    _name = 'project.include'

    parent_project_id = fields.Many2one('project.project')
    parent_task_id = fields.Many2one('project.task') #todo domain only on parent project
    duplicate = fields.Boolean(default=True)

    @api.multi
    def project_include(self):
        self.ensure_one()
        active_project_id = self.env['project.project'].browse(
            self._context['active_id'])
        if self.duplicate:
            # duplicate tasks setting new parent_project_id
            for task in self.env['project.task'].search(
                    [('project_id', '=', self._context['active_id']),
                     ('active', '=', False)]):
                new_task = task.copy(default={
                    'name': task.name,
                    'project_id': self.parent_project_id.id,
                    'date_start': self.parent_task_id.date_end and
                                  self.parent_task_id.date_end or
                                  self.parent_task_id.date_start and
                                  self.parent_task_id.date_start or fields.Date.today(),
                })
                new_task.parent_ids += self.parent_task_id
            # remove template project delegation from created tasks
            for task in self.env['project.task'].search(
                    [('project_id', '=', self.parent_project_id.id)]):
                for parent_task in task.parent_ids:
                    if parent_task.project_id == active_project_id:
                        task.parent_ids -= parent_task
                for child_task in task.child_ids:
                    if child_task.project_id == active_project_id:
                        task.child_ids -= child_task
        elif not self.duplicate:
            for task in self.env['project.task'].search(
                    [('project_id', '=', self._context['active_id'])]):
                task.project_id = self.parent_project_id
                task.parent_ids += self.parent_task_id
                task.date_start = self.parent_task_id.date_end and \
                    self.parent_task_id.date_end or \
                    self.parent_task_id.date_start and \
                    self.parent_task_id.date_start or fields.Date.today()

        return {
            'domain': "[('project_id','=', " + str(self.parent_project_id.id) + ")]",
            'name': 'Project',
            'view_type': 'kanban',
            'view_mode': 'kanban,tree,form',
            'res_model': 'project.task',
            'type': 'ir.actions.act_window',
            'target': 'current',
        }