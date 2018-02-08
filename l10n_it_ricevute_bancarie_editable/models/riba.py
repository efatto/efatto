# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class RibaListLine(models.Model):
    _inherit = 'riba.distinta.line'

    @api.one
    def _get_line_values(self):
        self.amount = 0.0
        self.invoice_date = ""
        self.invoice_number = ""
        for move_line in self.move_line_ids:
            self.amount += move_line.amount
            if not self.invoice_date:
                self.invoice_date = str(fields.Date.from_string(
                    move_line.move_line_id.invoice.date_invoice if
                    move_line.move_line_id and
                    move_line.move_line_id.invoice else
                    fields.Date.today()
                ).strftime('%d/%m/%Y'))
            else:
                self.invoice_date = "%s, %s" % (
                    self.invoice_date, str(fields.Date.from_string(
                        move_line.move_line_id.invoice.date_invoice if
                        move_line.move_line_id and
                        move_line.move_line_id.invoice else
                        fields.Date.today()
                    ).strftime('%d/%m/%Y')))
            if not self.invoice_number:
                self.invoice_number = str(
                    move_line.move_line_id.invoice.internal_number)
            else:
                self.invoice_number = "%s, %s" % (self.invoice_number, str(
                    move_line.move_line_id.invoice.internal_number))

    amount = fields.Float(
        compute='_get_line_values')
    invoice_date = fields.Char(
        compute='_get_line_values')
    invoice_number = fields.Char(
        compute='_get_line_values')