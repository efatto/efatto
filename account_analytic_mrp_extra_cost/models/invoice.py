
from odoo import models, fields, api


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    exclude_from_actual_cost = fields.Boolean(
        "No Actual Cost"
    )

    @api.one
    def button_exclude_from_actual_cost(self):
        self.exclude_from_actual_cost = not self.exclude_from_actual_cost
