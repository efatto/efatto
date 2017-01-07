# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _


class ProjectIssue(models.Model):
    _inherit = 'project.issue'

    @api.multi
    def write(self, vals):
        if vals.get('project_id', False) and not vals.get(
                'analytic_account_id', False):
            project = self.env['project.project'].browse(
                vals.get('project_id'))
            account = project.analytic_account_id
            if account:
                vals['analytic_account_id'] = account.id

        return super(ProjectIssue, self).write(vals)
