# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class PurchaseRequestLine(models.Model):
    _inherit = 'purchase.request.line'

    group_id = fields.Many2one('procurement.group')
    origin = fields.Char(related='')
    sale_order_id = fields.Many2one(
        comodel_name='sale.order',
        compute='_compute_sale_order_id',
        store=True,
    )
    sale_partner_id = fields.Many2one(
        related='sale_order_id.partner_id',
        store=True,
    )
    sale_order_line_id = fields.Many2one(
        comodel_name='sale.order.line',
        compute='_compute_sale_order_line_id',
        store=True,
    )
    sale_commitment_date = fields.Datetime(
        related='sale_order_line_id.commitment_date',
        store=True,
    )

    @api.multi
    @api.depends('group_id')
    def _compute_sale_order_id(self):
        for line in self:
            sale_order = self.env['sale.order']
            if line.group_id:
                sale_order = sale_order.search([
                    ('procurement_group_id', '=', line.group_id.id)
                ], limit=1)
            line.sale_order_id |= sale_order

    @api.multi
    @api.depends('group_id', 'product_id', 'product_qty')
    def _compute_sale_order_line_id(self):
        for line in self:
            sale_order_line = self.env['sale.order.line']
            # in case of a sale order with more line of the same product with the same
            # quantity, this method will link always the first found
            # The field date_required is computed and does not match in a field in sale
            # order line, sadly
            if line.group_id:
                sale_order_line = sale_order_line.search([
                    ('product_id', '=', line.product_id.id),
                    ('order_id.procurement_group_id', '=', line.group_id.id),
                    ('product_uom_qty', '=', line.product_qty),
                ], limit=1)
            line.sale_order_line_id |= sale_order_line


class StockRule(models.Model):
    _inherit = 'stock.rule'

    @api.multi
    def create_purchase_request(self, product_id, product_qty, product_uom,
                                origin, values):
        values.update(origin=origin)
        res = super().create_purchase_request(
            product_id, product_qty, product_uom, origin, values)
        return res

    @api.model
    def _prepare_purchase_request_line(self, request_id, product_id,
                                       product_qty, product_uom, values):
        res = super()._prepare_purchase_request_line(
            request_id, product_id, product_qty, product_uom, values)
        if values.get('origin'):
            res.update(origin=values['origin'])
        if values.get('group_id'):
            res.update(group_id=values['group_id'].id)
        return res
