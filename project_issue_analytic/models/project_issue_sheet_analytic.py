# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _


class ProjectIssue(models.Model):
    _inherit = 'project.issue'

    @api.multi
    def write(self, vals):
        for issue in self:
            if issue.project_id and not issue.analytic_account_id:
                issue.analytic_account_id = \
                    issue.project_id.analytic_account_id

        return super(ProjectIssue, self).write(vals)
