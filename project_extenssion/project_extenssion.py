# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import _
from openerp.exceptions import Warning
from openerp.osv import fields, osv
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class task(osv.osv):
    _inherit = 'project.task'

    def action_report_send(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        template_ids = self.pool['email.template'].search(cr, uid,[('model', '=', 'project.task')], limit=1)
        template_id = False
        if template_ids:
            template_id = template_ids[0]
        ir_model_data = self.pool.get('ir.model.data')
        compose_form_id = False
        compose_form = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')
        if compose_form:
            compose_form_id = compose_form[1]
        ctx = dict(context)
        ctx.update({
            'default_model': 'project.task',
            'default_res_id': ids[0],
            'default_use_template': template_id and True,
            'default_template_id': template_id and template_id or False,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    _columns = {
        'date_work_started': fields.datetime('New work start date'),
        'done': fields.text('Done'),
        'work_started': fields.boolean('Work Started'),
        'work_user_id': fields.many2one('res.users', 'Working User'),
    }
    _defaults = {
        'work_started': False,
    }

    def do_start_work(self, cr, uid, ids, context=None):
        for task in self.browse(cr, uid, ids, context):
            if not task.work_started:
                self.write(cr, uid, ids, {
                    'work_started': True, 'date_work_started': datetime.now(),
                    'work_user_id': uid,
                })
        return True

    def do_close_work(self, cr, uid, ids, context=None):
        for task in self.browse(cr, uid, ids):
            if uid != task.work_user_id.id:
                raise Warning(_('Task can be stopped only from creator user: %s')
                              % task.work_user_id.name)
                return False
            self.write(cr, uid, [task.id], {'work_started': False})
            duration = datetime.now() - datetime.strptime(task.date_work_started, DEFAULT_SERVER_DATETIME_FORMAT)
            duration_minuts = int(duration.total_seconds()/60)
            duration_hours = duration_minuts/60.0
            company_id = self.pool['res.users'].browse(cr, uid, uid, context).company_id
            now = fields.datetime.now()
            today = datetime.now().strftime("%d/%m/%Y")
            if duration_hours:
                self.pool.get('project.task.work').create(cr, uid, {
                    'name': _('Work of the day ') + today,
                    'date': now,
                    'hours': duration_hours,
                    'user_id': uid,
                    'company_id': company_id.id,
                    'task_id': task.id,
                    })

                remain_final = task.remaining_hours - duration_hours
                self.write(cr, uid, [task.id], {'remaining_hours': remain_final})
            return True

    def write(self, cr, uid, ids, vals, context=None):
            if vals.get('remaining_hours', False):
                vals['remaining_hours'] = round(vals['remaining_hours'], 2)
            res = super(task, self).write(cr, uid, ids, vals, context=context)

            return res


class project_task_history(osv.osv):
    _inherit = 'project.task.history'

    _columns = {
        'state': fields.selection([('draft', 'New'), ('cancelled', 'Cancelled'),('open', 'In Progress'),('pending', 'Pending'), ('done', 'Done')], 'Status'),
    }
