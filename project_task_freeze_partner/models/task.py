# -*- coding: utf-8 -*-

from odoo import api, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.onchange('project_id')
    def _onchange_project(self):
        pass
