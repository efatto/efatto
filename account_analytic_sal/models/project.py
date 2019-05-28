# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions


class ProjectProject(models.Model):
    _inherit = 'project.project'

    favorite_user_ids = fields.Many2many(
        'res.users', 'project_user_rel', 'project_id', 'uid', 'Project Members'
    )
