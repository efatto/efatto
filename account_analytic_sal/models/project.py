# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.multi
    def write(self, values):
        # when sale_line_id is changed, update all account.analytic.line linked to the
        # task. N.B.: so_line must be put in account.analytic_line to update qty
        # consigned
        if self._context.get('create', False) or 'sale_line_id' not in values:
            return super(ProjectTask, self).write(values)

        res = super(ProjectTask, self).write(values)
        for task in self:
            if task.sale_line_id:
                analytic_lines = self.env['account.analytic.line'].search([
                    ('task_id', '=', task.id),
                ])
                analytic_lines.write({'so_line': task.sale_line_id.id})
        return res
