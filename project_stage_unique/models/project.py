from odoo import _, api, models
from odoo.exceptions import UserError


class ProjectTaskType(models.Model):
    _inherit = "project.task.type"

    @api.constrains("name")
    def _constrains_name_unique(self):
        for rec in self:
            if self.search_count([("name", "=", rec.name), ("id", "!=", rec.id)]):
                raise UserError(_("A task type with the same name already exists!"))
