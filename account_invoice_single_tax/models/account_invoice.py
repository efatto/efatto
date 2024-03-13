from odoo import _, models
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = "account.move"

    def single_invoice_line_tax(self):
        errors = []
        for invoice in self.filtered(lambda x: x.is_invoice()):
            for invoice_line in invoice.invoice_line_ids:
                if len(invoice_line.tax_ids) != 1:
                    error_string = "[%s] %s \n" % (invoice.name, invoice_line.name)
                    errors.append(error_string)
        if errors:
            raise UserError(
                _("Multiple/None Taxes Defined in lines: %s")
                % ",".join(x for x in errors)
            )

    def _post(self, soft=True):
        self.single_invoice_line_tax()
        res = super()._post(soft=soft)
        return res
