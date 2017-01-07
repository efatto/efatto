# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _


class ProjectIssue(models.Model):
    _inherit = 'project.issue'

    @api.multi
    def write(self, vals):
        if self.project_id:
            account = self.project_id.analytic_account_id
            vals['analytic_account_id'] = account
        if self.ids:
            # Write works when record backed by real db row:
            super(ProjectIssue, self).write(vals)
        else:
            # Update is needed when called from onchange:
            self.update(vals)
