# -*- coding: utf-8 -*-

from odoo import models, fields


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_invoice_policy = fields.Selection(
        related='product_id.invoice_policy', readonly=True)
    product_track_service = fields.Selection(
        related='product_id.track_service', readonly=True)
