# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import fields, api, models, _


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.multi
    def onchange_user_id(self, user_id):
        vals = {}
        # remove change of date_start when assigned
        # if user_id:
        #     vals['date_start'] = fields.datetime.now()
        return {'value': vals}
