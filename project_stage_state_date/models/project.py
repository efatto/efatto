# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from odoo import models, fields, api


class Project(models.Model):
    _inherit = "project.project"

    def _active_task_count(self):
        for project in self:
            project.task_count = len(project.task_ids.filtered(
                lambda x: x.state not in ['done', 'cancelled']))

    task_count = fields.Integer(
        string='Active tasks',
        compute='_active_task_count')
