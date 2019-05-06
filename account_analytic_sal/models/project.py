# -*- coding: utf-8 -*-

from odoo import models, fields


class Task(models.Model):
    _inherit = 'project.task'

    planned_hours = fields.Float(groups='project.group_project_manager')
