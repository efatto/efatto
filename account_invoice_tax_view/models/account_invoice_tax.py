# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class AccountInvoiceTax(models.Model):
    _inherit = "account.invoice.tax"

    base_esclusa = fields.Boolean(
        string='Imponibile Esclusa',
        related='base_code_id.spesometro_escludi',
    )
    vat_esclusa = fields.Boolean(
        string='IVA Esclusa',
        related='tax_code_id.spesometro_escludi',
    )
    partner_id = fields.Many2one(
        string='Partner',
        related='invoice_id.partner_id',
    )
    vat = fields.Char(
        string='VAT',
        related='invoice_id.partner_id.vat',
    )
    fiscalcode = fields.Char(
        string='C.F.',
        related='invoice_id.partner_id.fiscalcode',
    )
    journal_id = fields.Many2one(
        string='Giornale',
        related='invoice_id.journal_id',
    )