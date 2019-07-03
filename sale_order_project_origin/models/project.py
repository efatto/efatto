# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _


class ProjectProject(models.Model):
    _inherit = "project.project"

    origin = fields.Char(string="Origin")

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        res = super(ProjectProject, self).name_search(
            name, args=args, operator=operator, limit=limit)
        if args is None:
            args = []
        args += [('origin', operator, name)]
        ids = self.search(args, limit=limit)
        if ids:
            return ids.name_get()
        return res


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    def _get_project(self):
        project = super(ProcurementOrder, self)._get_project()
        if self.sale_line_id:
            project.origin = self.sale_line_id.order_id.origin
        return project
