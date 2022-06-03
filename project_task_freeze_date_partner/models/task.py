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
        if vals['value'].get('date_start', False):
            vals['value'].pop('date_start')
        return vals

    @api.cr_uid_id_context
    def onchange_project(self, cr, uid, id, project_id, context):
        vals = super(ProjectTask, self).onchange_project(
            cr, uid, id, project_id=project_id, context=context
        )
        if vals.get('value', False):
            if vals['value'].get('partner_id', False):
                vals['value'].pop('partner_id')
        return vals
