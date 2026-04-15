from odoo import models


class ProjectTaskType(models.Model):
    _inherit = "project.task.type"

    _sql_constraints = [
        ("name_uniq", "unique (name)", "Name must be unique"),
    ]
