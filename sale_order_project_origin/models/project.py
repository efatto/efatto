# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class ProjectProject(models.Model):
    _inherit = "project.project"

    origin = fields.Char(string="Origin")

#     @api.model
#     def name_search(self, name, args=None, operator='ilike', limit=100):
#         res = super(ProjectProject, self).name_search(
#             name, args=args, operator=operator, limit=limit)
#         if args is None:
#             args = []
#         args += [('origin', operator, name)]
#         ids = self.search(args, limit=limit)
#         if ids:
#             return ids.name_get()
#         return res
#
#
# class ProcurementOrder(models.Model):
#     _inherit = 'procurement.order'
#
#     def _get_project(self):
#         project = super(ProcurementOrder, self)._get_project()
#         if self.sale_line_id:
#             if not project:
#                 project = self.env['project.project'].with_context(
#                     active_test=False).search([
#                         ('name', '=', self.sale_line_id.order_id.
#                          unrevisioned_name)
#                     ])
#             if project:
#                 project.origin = self.sale_line_id.order_id.origin
#         return project
