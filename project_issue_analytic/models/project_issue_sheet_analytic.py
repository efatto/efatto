# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _


class ProjectIssue(models.Model):
    _inherit = 'project.issue'

    @api.multi
    @api.onchange('project_id')
    def on_change_project(self):
        if self.project_id:
            account = self.project_id.analytic_account_id
            if account:
                self.analytic_account_id = account
