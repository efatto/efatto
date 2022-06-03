# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, _
from openerp.exceptions import Warning


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    @api.multi
    def action_sign_in(self):
        try:
            self.attendance_action_change()
        except Exception, e:
            raise Warning(_(e))
        return True

    @api.multi
    def action_sign_out(self):
        try:
            self.attendance_action_change()
        except Exception, e:
            raise Warning(_(e))
        return True

    @api.multi
    def print_weekly_hours_report(self):
        wizard_id = self.env['ir.model.data'].get_object_reference(
            'employee_check_inout', 'wizard_weekly_hours_form_view')[1]
        if wizard_id:
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'wizard.weekly.hours',
                'view_id': wizard_id,
                'target': 'new'
            }
