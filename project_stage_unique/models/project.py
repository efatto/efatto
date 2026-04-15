from odoo import models


class ProjectTaskType(models.Model):
    _inherit = "project.task.type"

    _sql_constraints = [
        ("name_uniq", "UNIQUE (name)", "Name must be unique"),
    ]
