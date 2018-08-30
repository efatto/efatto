# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    _sql_constraints = [(
        'name_project_task_type_uniq',
        'unique(name)',
        'A task type with the same name already exists for this company !'
        )]
