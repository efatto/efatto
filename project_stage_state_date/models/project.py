# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class Project(models.Model):
    _inherit = "project.project"

    @api.one
    def _active_task_count(self):
        count = 0
        for task in self.tasks:
            if task.state not in ['done', 'cancelled']:
                count += 1
        self.task_count = count

    task_count = fields.Integer(
        'Active tasks',
        compute='_active_task_count')
