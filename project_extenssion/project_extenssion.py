# -*- coding: utf-8 -*-

from openerp import _
from openerp.osv import fields, osv
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


_TASK_STATE = [('draft', 'New'),('open', 'In Progress'),('pending', 'Pending'), ('done', 'Done'), ('cancelled', 'Cancelled')]


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
        'state': fields.related('stage_id', 'state', type="selection", store=True,
                selection=_TASK_STATE, string="Status", readonly=True,
                help='The status is set to \'Draft\', when a case is created.\
                      If the case is in progress the status is set to \'Open\'.\
                      When the case is over, the status is set to \'Done\'.\
                      If the case needs to be reviewed then the status is \
                      set to \'Pending\'.'),
    }
    _defaults = {
        'work_started': False,
    }

    def do_start_work(self, cr, uid, ids):
        for task in self.browse(cr, uid, ids):
            if not task.work_started:
                self.write(cr, uid, ids, {
                    'work_started': True, 'date_work_started': datetime.now()
                })
        return True

    def do_close_work(self, cr, uid, ids, context=None):
        for task in self.browse(cr, uid, ids):
            self.write(cr, uid, [task.id], {'work_started': False})
            duration = datetime.now() - datetime.strptime(task.date_work_started, DEFAULT_SERVER_DATETIME_FORMAT)
            duration_hours = duration.total_seconds()/3600
            company_id = self.pool['res.users'].browse(cr, uid, uid, context).company_id

            self.pool.get('project.task.work').create(cr, uid, {
                'name': _('Work of the day ') + str(datetime.now())[:10],
                'date': str(datetime.now())[:10],
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


class project_task_type(osv.osv):
    _inherit = 'project.task.type'

    _columns = {
        'state': fields.selection(
            _TASK_STATE, 'Related Status', required=False,
            help="The status of your document is automatically changed regarding the selected stage. "
            "For example, if a stage is related to the status 'Close', when your document reaches this stage, it is automatically closed."),
    }

