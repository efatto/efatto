from odoo import api, fields, models


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    exclude_extra_cost = fields.Boolean("No Actual Cost")

    @api.one
    def button_exclude_extra_cost(self):
        self.exclude_extra_cost = not self.exclude_extra_cost
