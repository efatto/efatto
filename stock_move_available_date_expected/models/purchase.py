# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    tag_ids = fields.Many2many(
        'purchase.order.tag',
        compute='_compute_tag_ids',
        inverse='_inverse_tag_ids',
        string="Tag", copy=False, store=True)
    color = fields.Integer(
        compute='_compute_color',
        store=True)

    @api.multi
    @api.depends('tag_ids')
    def _compute_color(self):
        for order in self:
            if order.tag_ids:
                order.color = order.tag_ids[0].color
            else:
                order.color = False

    @api.multi
    def _inverse_tag_ids(self):
        for order in self:
            for tag in order.tag_ids:
                tag.order_state = order.state

    @api.multi
    @api.depends('state')
    def _compute_tag_ids(self):
        for order in self:
            tag_ids = self.env['purchase.order.tag'].search([
                ('order_state', '=', order.state)
            ])
            if tag_ids:
                order.tag_ids = tag_ids.ids
            else:
                order.tag_ids = False
2