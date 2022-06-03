# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.depends('state')
    @api.one
    def get_progress(self):
        # state: 'draft' 'cancelled' 'open' 'done' 'pending'
        progress = 0.0
        if self.state in ['cancelled', 'done']:
            progress = 100
        elif self.state == 'open':
            if self.date_end and self.date_start:
                if fields.Date.from_string(self.date_end) > \
                        fields.Date.from_string(fields.Date.today()) > \
                        fields.Date.from_string(self.date_start):
                    duration_passed = (fields.Date.from_string(
                        fields.Date.today()) - fields.Date.from_string(
                        self.date_start))
                    duration_total = (fields.Date.from_string(self.date_end) -
                                      fields.Date.from_string(self.date_start))
                    progress = duration_passed.total_seconds() / \
                               duration_total.total_seconds() * 100
        else:
            progress = 0

        self.progress_state = progress

    progress_state = fields.Float('Progress on date', compute='get_progress')
