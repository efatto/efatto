# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_invoice_policy = fields.Selection(
        related='product_id.invoice_policy', readonly=True)
    product_service_policy = fields.Selection(
        related='product_id.service_policy', readonly=True)
    product_service_tracking = fields.Selection(
        related='product_id.service_tracking', readonly=True)
