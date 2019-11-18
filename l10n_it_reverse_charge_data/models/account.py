# -*- coding: utf-8 -*-

from openerp import api, fields, models


class account_invoice(models):
    _inherit = 'account.invoice'

    rc_self_invoice_id = fields.Many2one(
        'account.invoice', 'Auto Invoice', oldname='auto_invoice_id',
        ondelete="set null")
