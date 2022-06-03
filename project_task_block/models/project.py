# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _
from openerp.exceptions import Warning, ValidationError


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.multi
    def write(self, vals):
        def get_recursive_parent(task):
            for parent in task.parent_ids:
                if parent.kanban_state == 'blocked':
                    raise Warning(_('Blocked task parent %s') % parent.name)
                    return False
                if parent.parent_ids:
                    for parent_task in parent.parent_ids:
                        if parent_task.kanban_state == 'blocked':
                            raise Warning(_('Blocked task parent %s') %
                                parent_task.name)
                            return False
                        get_recursive_parent(parent_task)
        for task in self:
            get_recursive_parent(task)

        return super(ProjectTask, self).write(vals)
