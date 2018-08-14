# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from odoo import fields, api, models, _


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.onchange('project_id')
    def _onchange_project(self):
        pass
