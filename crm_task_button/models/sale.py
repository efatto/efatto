# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import fields, api, models, _


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    task_count = fields.Integer(related='partner_id.task_count')

    @api.multi
    def action_open_task_calendar_week(self):
        self.ensure_one()
        context = self._context.copy()
        context.update({
            'search_default_partner_id': self.partner_id.id,
            'default_partner_id': self.partner_id.id,
        })
        view_calendar_id = self.env.ref(
            'project_task_state_color.'
            'view_task_calendar_partner_shipping_color')
        view_tree_id = self.env.ref('project.view_task_tree2')
        view_form_id = self.env.ref('project.view_task_form2')
        return {
            'name': _('Tasks'),
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
            'view_mode': 'calendar',
            'view_type': 'calendar',
            'views': [(view_calendar_id.id, 'calendar'),
                      (view_tree_id.id, 'tree'),
                      (view_form_id.id, 'form'),
                      ],
            'view_id': False,
            'context': context,
        }
