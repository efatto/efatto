# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _


class ProjectIssue(models.Model):
    _inherit = 'project.issue'

    @api.multi
    def write(self, vals):
        if self.project_id and not self.analytic_account_id:
            self.analytic_account_id = self.project_id.analytic_account_id

        return super(ProjectIssue, self).write(vals)
