# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import fields, api, models, _


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.cr_uid_ids_context
    def onchange_user_id(self, cr, uid, ids, user_id, context):
        vals = super(ProjectTask, self).onchange_user_id(
            cr, uid, ids, user_id=user_id, context=context
        )
        vals = {}
        task = self.browse(cr, uid, ids, context=context)
        if user_id:
            vals['date_start'] = task.date_start if task.date_start else \
                fields.datetime.now()
        return {'value': vals}

    @api.multi
    def write(self, vals):
        if vals.get('user_id') and self.date_start \
                and 'date_start' not in vals:
            vals['date_start'] = self.date_start
        return super(ProjectTask, self).write(vals)
