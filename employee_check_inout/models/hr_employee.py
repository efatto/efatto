# -*- encoding: utf-8 -*-
##############################################################################
#    Copyright (c) 2012 - Present Acespritech Solutions Pvt. Ltd. All Rights Reserved
#    Author: <info@acespritech.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of the GNU General Public License is available at:
#    <http://www.gnu.org/licenses/gpl.html>.
#
##############################################################################

from openerp import fields, models, api, _
from openerp.exceptions import Warning


class hr_employee(models.Model):
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
        wizard_id = self.env['ir.model.data'].get_object_reference('employee_check_inout', 'wizard_weekly_hours_form_view')[1]
        if wizard_id:
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'wizard.weekly.hours',
                'view_id': wizard_id,
                'target': 'new'
            }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: