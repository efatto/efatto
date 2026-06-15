from odoo import api, models
from odoo.exceptions import UserError


class ProjectTaskType(models.Model):
    _inherit = "project.task.type"

    @api.constrains("name")
    def _constrains_name_unique(self):
        for rec in self:
            lang = (
                rec.user_id.company_id.partner_id.lang
                or self.env.company.partner_id.lang
                or self.env.lang
                or "en_US"
            )
            rec_name = rec.with_context(lang=lang).name
            if self.with_context(lang=lang).search_count(
                [("name", "=", rec_name), ("id", "!=", rec.id)]
            ):
                raise UserError(
                    self.env._("A task type with the same name already exists!")
                )
