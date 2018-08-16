# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta


class ProjectProject(models.Model):
    _inherit = 'project.project'

    task_current_week_count = fields.Integer(
        compute='_compute_task_current_week_count',
        string='Tasks current week')

    def _compute_task_current_week_count(self):
        for project in self:
            project.task_current_week_count = len(
                project.task_ids.filtered(
                    lambda x:
                    (fields.Date.from_string(fields.Date.today())
                     - relativedelta(weeks=1, weekday=0)) <=
                    fields.Date.from_string(x.date_start)
                    <= (fields.Date.from_string(fields.Date.today())
                        + relativedelta(weeks=0, weekday=6))
                )
            )
