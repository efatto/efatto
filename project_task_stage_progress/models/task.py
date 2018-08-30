# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from odoo import fields, api, models, _
from odoo.exceptions import UserError


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    @api.constrains('user_assign')
    def _check_user_assign_task_type(self):
        for stage in self.filtered(lambda x: x.user_assign):
            for project in stage.project_ids:
                if len(project.type_ids.filtered(lambda y: y.user_assign)
                       ) > 1:
                    raise UserError(
                        _('Only 1 task of type "User assign" can be marked in '
                          'a project.'))

    user_assign = fields.Boolean()


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.onchange('user_id')
    def _onchange_user(self):
        if self.user_id:
            self.stage_id = self.project_id.type_ids.filtered(
                lambda x: x.user_assign)
