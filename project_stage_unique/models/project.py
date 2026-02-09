from odoo import models


class ProjectTaskType(models.Model):
    _inherit = "project.task.type"

    # @api.constrains("name")
    # def _constrains_name_unique(self):
    #     for rec in self:
    #         if self.search_count([("name", "=", rec.name), ("id", "!=", rec.id)]):
    #             raise UserError(_("A task type with the same name already exists!"))

    _sql_constraints = [
        (
            "name_first_lang_uniq",
            "UNIQUE (name->>'en_US')",
            "Task type name must be unique.",
        )
    ]
