# -*- coding: utf-8 -*-

from openerp import models, fields


class ProjectProject(models.Model):
    _inherit = 'project.project'

    favorite_user_ids = fields.Many2many(
        related='members', string='Project Members')
