from odoo import models


class ProjectProject(models.Model):
    _inherit = "project.project"

    def write(self, values):
        if "sale_line_id" in values and not values["sale_line_id"]:
            if self.bill_type == "customer_task" and not self.sale_line_id:
                values.pop("sale_line_id")
        return super().write(values)
