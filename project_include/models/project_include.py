# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _


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
            task.parent_ids += self.parent_task_id
            task.date_start = self.parent_task_id.date_end and \
                self.parent_task_id.date_end or \
                self.parent_task_id.date_start and \
                self.parent_task_id.date_start or fields.Date.today()
        # self.env['project.project'].browse(self._context['active_id']).unlink()
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