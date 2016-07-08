# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _
from openerp.exceptions import Warning, ValidationError
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from dateutil import relativedelta


class WizardProjectInclude(models.TransientModel):
    _name = 'project.include'

    parent_project_id = fields.Many2one('project.project')
    parent_task_id = fields.Many2one('project.task') #todo domain only on parent project

    @api.multi
    def project_include(self):
        self.ensure_one()
        for task in self.env['project.task'].search(
                [('project_id', '=', self._context['active_id'])]):
            task.project_id = self.parent_project_id
        #
        #     new_date_start = datetime.strftime('%Y-%m-%d')
        #     new_date_end = False
        #     if proj.date_start and proj.date:
        #         start_date = datetime(*datetime.strptime(proj.date_start, '%Y-%m-%d')[:3])
        #         end_date = datetime(*datetime.strptime(proj.date, '%Y-%m-%d')[:3])
        #         new_date_end = (
        #         datetime(*datetime.strptime(new_date_start, '%Y-%m-%d')[:3]) + (
        #         end_date - start_date)).strftime('%Y-%m-%d')
        #
        #     new_id = self.with_env({'copy': True, 'analytic_project_copy': True}).copy(proj.id, default={
        #         'name': _("%s (copy)") % proj.name,
        #         'state': 'open',
        #         'date_start': new_date_start,
        #         'date': new_date_end,
        #         'parent_id': parent_id})
        #     result.append(new_id.id)
        #
        #     child_ids = self.search([
        #         ('parent_id', '=', proj.analytic_account_id.id)])
        #     parent_id = self.read(self._cr, self._uid, new_id, ['analytic_account_id'])[
        #         'analytic_account_id'][0]
        #     if child_ids:
        #         self.duplicate_template(self._cr, self._uid, child_ids,
        #                                 context={'parent_id': parent_id})
        #
        # data_obj = self.env['ir.model.data']
        # if result and len(result):
        #     res_id = result[0]
        #     form_view_id = data_obj._get_id(self._cr, self._uid, 'project', 'edit_project')
        #     form_view = data_obj.read(self._cr, self._uid, form_view_id, ['res_id'])
        #     tree_view_id = data_obj._get_id(self._cr, self._uid, 'project', 'view_project')
        #     tree_view = data_obj.read(self._cr, self._uid, tree_view_id, ['res_id'])
        #     search_view_id = data_obj._get_id(self._cr, self._uid, 'project',
        #                                       'view_project_project_filter')
        #     search_view = data_obj.read(self._cr, self._uid, search_view_id, ['res_id'])
        #     return {
        #         'name': _('Projects'),
        #         'view_type': 'form',
        #         'view_mode': 'form,tree',
        #         'res_model': 'project.project',
        #         'view_id': False,
        #         'res_id': res_id,
        #         'views': [(form_view['res_id'], 'form'),
        #                   (tree_view['res_id'], 'tree')],
        #         'type': 'ir.actions.act_window',
        #         'search_view_id': search_view['res_id'],
        #         'nodestroy': True
        #     }

#
# @api.multi
# def load_template(self):
#
#     moves = {}
#     for line in self.template_id.template_line_ids:
#         if line.journal_id.id not in moves:
#             moves[line.journal_id.id] = self._make_move(
#                 self.template_id.name,
#                 period.id,
#                 line.journal_id.id,
#                 self.partner_id.id
#             )
#
#         self._make_move_line(
#             line,
#             computed_lines,
#             moves[line.journal_id.id],
#             period.id,
#             self.partner_id.id
#         )
#         if self.template_id.cross_journals:
#             trans_account_id = self.template_id.transitory_acc_id.id
#             self._make_transitory_move_line(
#                 line,
#                 computed_lines,
#                 moves[line.journal_id.id],
#                 period.id,
#                 trans_account_id,
#                 self.partner_id.id
#             )
#
#     return {
#         'domain': "[('id','in', " + str(moves.values()) + ")]",
#         'name': 'Entries',
#         'view_type': 'form',
#         'view_mode': 'tree,form',
#         'res_model': 'account.move',
#         'type': 'ir.actions.act_window',
#         'target': 'current',
#     }