# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _


class ProjectIssue(models.Model):
    _inherit = 'project.issue'

    analytic_ids = fields.Many2many(
        comodel_name='account.analytic.account',
        relation='project_issue_account_analytic_rel',
        column1='issue_id', column2='account_id',
        string='Analytic accounts',
    )

    @api.cr_uid_ids_context
    def on_change_project(self, cr, uid, ids, project_id, context=None):
        if not project_id:
            return {}

        result = super(ProjectIssue, self).on_change_project(cr, uid, ids,
                                                              project_id,
                                                              context=context)

        project = self.pool.get('project.project').browse(cr, uid, project_id,
                                                          context=context)
        if 'value' not in result:
            result['value'] = {}

        account = project.analytic_account_id
        if account:
            if account.type == 'view':
                result['value']['analytic_ids'] = project.analytic_account_id.\
                    child_ids.mapped('id')
            else:
                result['value']['analytic_ids'] = [account.id]
            result['value']['analytic_account_id'] = account.id

        return result
