# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api


class ProjectIssue(models.Model):
    _inherit = 'project.issue'

    @api.model
    def create(self, values):
        if values.get('project_id', False) and not \
                values.get('analytic_account_id', False):
            project = self.env['project.project'].browse(
                values.get('project_id'))
            if project:
                values['analytic_account_id'] = project.analytic_account_id.id
        return super(ProjectIssue, self).create(values)
