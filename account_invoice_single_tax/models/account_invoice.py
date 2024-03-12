from odoo import _, models
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = "account.move"

    def single_invoice_line_tax(self):
        errors = []
        for invoice in self:
            for invoice_line in invoice.invoice_line_ids:
                if len(invoice_line.tax_ids) != 1:
                    error_string = "%s-%s \n" % (invoice.name, invoice_line.name)
                    errors.append(error_string)
        if errors:
            errors_full_string = ",".join(x for x in errors)
            raise UserError(
                _("Multiple/None Taxes Defined in lines: %s") % errors_full_string
            )
        else:
            return True

    def action_post(self):
        self.single_invoice_line_tax()
        res = super().action_post()
        return res
