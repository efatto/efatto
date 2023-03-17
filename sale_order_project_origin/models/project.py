# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields


class ProjectProject(models.Model):
    _inherit = "project.project"

    origin = fields.Char(string="Origin")
